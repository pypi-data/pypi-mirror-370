import httpx
import xmltodict
from typing import List, Dict, Any, Optional
from .base import DirectoryTreeProvider
from loguru import logger


class BinanceDirectoryTreeProvider(DirectoryTreeProvider):
    """Directory tree provider for Binance."""

    def __init__(self):
        self.base_url = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
        self.download_url_prefix = "https://data.binance.vision/"

    def get_download_url_prefix(self) -> str:
        """Get the download URL prefix for Binance.

        Returns:
            str: Download URL prefix
        """
        return self.download_url_prefix

    def _get(self, url: str) -> str:
        """Make an HTTP GET request.

        Args:
            url (str): URL to request

        Returns:
            str: Response text
        """
        # Set a longer timeout for directory listing operations
        timeout = httpx.Timeout(60.0, connect=30.0, read=60.0)

        # Use a retry count of 3 by default
        retry_count = 3

        for attempt in range(retry_count + 1):
            try:
                response = httpx.get(url, timeout=timeout)
                response.raise_for_status()
                return response.text
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                logger.error(
                    f"HTTP error on attempt {attempt + 1}/{retry_count + 1}: {e}"
                )

                if attempt < retry_count:
                    # Wait before retrying (exponential backoff)
                    wait_time = 2**attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    import time

                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Failed to get {url} after {retry_count + 1} attempts"
                    )
                    raise
            except Exception as e:
                logger.error(f"Unexpected error occurred: {e}")
                raise

    def get_directory_tree(self, path: str, max_retries: int = 3) -> List[str]:
        """Get directory tree from Binance.

        Args:
            path (str): Base path to get directory tree from
            max_retries (int, optional): Maximum number of retries for empty results. Defaults to 3.

        Returns:
            List[str]: List of paths
        """
        url = f"{self.base_url}?delimiter=/&prefix={path}"
        base_url = url
        results = []
        page_count = 0

        # Create a progress bar for directory listing
        from tqdm import tqdm

        progress_bar = tqdm(
            desc=f"Fetching directory {path}",
            unit="page",
            bar_format="{desc}: {n_fmt} pages [{elapsed}<{remaining}]",
        )

        try:
            # Main loop for retries
            for retry_attempt in range(max_retries + 1):
                if retry_attempt > 0:
                    logger.warning(
                        f"No results found for {path}, retry attempt {retry_attempt}/{max_retries}..."
                    )
                    progress_bar.reset()
                    url = base_url  # Reset URL to the base URL

                # Reset results for each retry
                if retry_attempt > 0:
                    results = []

                # Pagination loop
                while True:
                    # Get the raw XML response
                    raw_xml = self._get(url)

                    # Log the raw XML for debugging (truncated to avoid excessive logging)
                    xml_preview = (
                        raw_xml[:500] + "..." if len(raw_xml) > 500 else raw_xml
                    )
                    logger.debug(f"Raw XML response for {url}: {xml_preview}")

                    # Parse the XML
                    try:
                        data = xmltodict.parse(raw_xml)
                        xml_data = data["ListBucketResult"]
                    except Exception as xml_error:
                        logger.error(f"XML parsing error: {xml_error}")
                        logger.error(f"Raw XML: {raw_xml}")
                        raise

                    page_count += 1
                    progress_bar.update(1)

                    # Update progress description with item count
                    progress_bar.set_description(
                        f"Fetching directory {path} ({len(results)} items)"
                    )

                    # Process CommonPrefixes (directories)
                    if "CommonPrefixes" in xml_data:
                        # Handle case when CommonPrefixes is a list
                        if isinstance(xml_data["CommonPrefixes"], list):
                            results.extend(
                                [x["Prefix"] for x in xml_data["CommonPrefixes"]]
                            )
                            logger.debug(
                                f"Added {len(xml_data['CommonPrefixes'])} CommonPrefixes"
                            )
                        # Handle case when CommonPrefixes is a single item
                        else:
                            results.append(xml_data["CommonPrefixes"]["Prefix"])
                            logger.debug(
                                f"Added 1 CommonPrefix: {xml_data['CommonPrefixes']['Prefix']}"
                            )

                    # Process Contents (files)
                    if "Contents" in xml_data:
                        # Handle case when Contents is a list
                        if isinstance(xml_data["Contents"], list):
                            results.extend([x["Key"] for x in xml_data["Contents"]])
                            logger.debug(f"Added {len(xml_data['Contents'])} Contents")
                        # Handle case when Contents is a single item
                        else:
                            results.append(xml_data["Contents"]["Key"])
                            logger.debug(
                                f"Added 1 Content: {xml_data['Contents']['Key']}"
                            )

                    # Check if we're done with pagination
                    if xml_data["IsTruncated"] == "false":
                        break

                    # Get the next page
                    if "NextMarker" in xml_data:
                        url = f"{base_url}&marker={xml_data['NextMarker']}"
                    else:
                        logger.warning(
                            f"No NextMarker found in response, but IsTruncated is not false"
                        )
                        break

                # If we found results, no need to retry
                if results:
                    break

            progress_bar.close()

            return results
        except Exception as e:
            progress_bar.close()
            logger.error(f"Error getting directory tree for {path}: {e}")
            raise

    def get_available_data_types(self) -> List[str]:
        """Get available data types from Binance.

        Returns:
            List[str]: List of available data types
        """
        paths = self.get_directory_tree("data/")
        # Extract data types (e.g., spot, futures, options)
        data_types = []
        for path in paths:
            parts = path.split("/")
            if len(parts) >= 2 and parts[0] == "data":
                data_types.append(parts[1])

        return list(set(data_types))  # Remove duplicates

    def get_available_intervals(self, data_type: str) -> List[str]:
        """Get available intervals for a data type.

        Args:
            data_type (str): Data type to get intervals for

        Returns:
            List[str]: List of available intervals
        """
        # For futures data type, we need to handle the cm/um subdirectories
        if data_type == "futures":
            # Get the futures subtypes (cm, um)
            futures_subtypes = self.get_directory_tree(f"data/{data_type}/")
            futures_subtypes = [
                path.split("/")[-2] for path in futures_subtypes if path.endswith("/")
            ]

            # Combine intervals from all futures subtypes
            intervals = []
            for subtype in futures_subtypes:
                subtype_paths = self.get_directory_tree(f"data/{data_type}/{subtype}/")
                for path in subtype_paths:
                    parts = path.split("/")
                    if (
                        len(parts) >= 4
                        and parts[0] == "data"
                        and parts[1] == data_type
                        and parts[2] == subtype
                    ):
                        # Store as "subtype/interval" (e.g., "cm/daily")
                        intervals.append(f"{subtype}/{parts[3]}")

            return list(set(intervals))  # Remove duplicates
        else:
            # For other data types (like spot), use the original logic
            paths = self.get_directory_tree(f"data/{data_type}/")
            # Extract intervals (e.g., daily, monthly)
            intervals = []
            for path in paths:
                parts = path.split("/")
                if len(parts) >= 3 and parts[0] == "data" and parts[1] == data_type:
                    intervals.append(parts[2])

            return list(set(intervals))  # Remove duplicates

    def get_available_symbols(self, data_type: str, interval: str) -> List[str]:
        """Get available symbols for a data type and interval.

        Args:
            data_type (str): Data type to get symbols for
            interval (str): Interval to get symbols for

        Returns:
            List[str]: List of available symbols
        """
        # For futures data type, handle the cm/um subdirectories
        if data_type == "futures" and "/" in interval:
            # Split the interval into subtype and actual interval
            subtype, actual_interval = interval.split("/")
            paths = self.get_directory_tree(
                f"data/{data_type}/{subtype}/{actual_interval}/"
            )

            # Extract symbols
            symbols = []
            for path in paths:
                parts = path.split("/")
                if (
                    len(parts) >= 5
                    and parts[0] == "data"
                    and parts[1] == data_type
                    and parts[2] == subtype
                    and parts[3] == actual_interval
                ):
                    symbols.append(parts[4])

            return list(set(symbols))  # Remove duplicates
        else:
            # For other data types, use the original logic
            paths = self.get_directory_tree(f"data/{data_type}/{interval}/")
            # Extract symbols
            symbols = []
            for path in paths:
                parts = path.split("/")
                if (
                    len(parts) >= 4
                    and parts[0] == "data"
                    and parts[1] == data_type
                    and parts[2] == interval
                ):
                    symbols.append(parts[3])

            return list(set(symbols))  # Remove duplicates
