import argparse
import logging
import os
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List


# Configure logging
def setup_logging(log_file: str = "download.log", log_level: str = "INFO"):
    """Setup logging configuration with custom log file"""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger(__name__)


logger = setup_logging()


class DownloadManager:
    def __init__(
        self,
        aws_path: str,
        output_path: str,
        file_extension: str = "jpg",
        max_workers: int = 50,
        max_retries: int = 3,
    ):
        self.aws_path = aws_path.rstrip("/")
        self.output_path = Path(output_path)
        self.file_extension = file_extension.lstrip(
            "."
        )  # Remove leading dot if present
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.downloaded_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.total_count = 0
        self._shutdown_requested = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Ensure output directory exists
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Validate AWS CLI is available
        self._validate_aws_cli()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self._shutdown_requested = True

    def _validate_aws_cli(self):
        """Validate that AWS CLI is installed and configured"""
        try:
            result = subprocess.run(
                ["aws", "--version"], capture_output=True, text=True, check=True
            )
            logger.info(f"AWS CLI version: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            logger.error("AWS CLI is not installed or not in PATH")
            sys.exit(1)
        except FileNotFoundError:
            logger.error("AWS CLI not found. Please install AWS CLI first.")
            sys.exit(1)

    def _download_with_retry(self, file_id: str) -> str:
        """Download a single file with retry logic
        Returns: 'downloaded', 'skipped', or 'failed'
        """
        output_file = self.output_path / f"{file_id}.{self.file_extension}"

        # Check if file already exists
        if output_file.exists():
            logger.debug(f"Skipped (already exists): {output_file.name}")
            return "skipped"

        s3_uri = f"{self.aws_path}/{file_id}.{self.file_extension}"

        for attempt in range(self.max_retries):
            if self._shutdown_requested:
                logger.info("Shutdown requested, stopping downloads")
                return False

            try:
                cmd = ["aws", "s3", "cp", s3_uri, str(output_file)]

                # Add timeout to prevent hanging
                result = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                )

                logger.info(f"Downloaded: {output_file.name}")
                return "downloaded"

            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout on attempt {attempt + 1} for {file_id}")
                if output_file.exists():
                    output_file.unlink()  # Remove partial download

            except subprocess.CalledProcessError as e:
                logger.warning(
                    f"Failed attempt {attempt + 1} for {file_id}: {e.stderr}"
                )
                if output_file.exists():
                    output_file.unlink()  # Remove partial download

                # Don't retry on certain errors
                if "NoSuchKey" in str(e.stderr) or "Access Denied" in str(e.stderr):
                    logger.error(f"File not found or access denied: {file_id}")
                    return "failed"

            except Exception as e:
                logger.error(f"Unexpected error downloading {file_id}: {e}")
                if output_file.exists():
                    output_file.unlink()

            # Wait before retry (exponential backoff)
            if attempt < self.max_retries - 1:
                wait_time = min(2**attempt, 30)  # Cap at 30 seconds
                time.sleep(wait_time)

        logger.error(f"Failed to download {file_id} after {self.max_retries} attempts")
        return "failed"

    def download_files(self, file_ids: List[str]) -> int:
        """Download multiple files using thread pool"""
        self.total_count = len(file_ids)
        logger.info(
            f"Starting download of {self.total_count} files with {self.max_workers} workers"
        )

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_id = {
                executor.submit(self._download_with_retry, file_id): file_id
                for file_id in file_ids
            }

            # Process completed tasks
            for future in as_completed(future_to_id):
                if self._shutdown_requested:
                    logger.info("Shutdown requested, cancelling remaining tasks")
                    break

                file_id = future_to_id[future]

                try:
                    result = future.result()
                    if result == "downloaded":
                        self.downloaded_count += 1
                    elif result == "skipped":
                        self.skipped_count += 1
                    else:  # 'failed'
                        self.failed_count += 1

                except Exception as e:
                    logger.error(f"Exception processing {file_id}: {e}")
                    self.failed_count += 1

                # Log progress
                completed = (
                    self.downloaded_count + self.failed_count + self.skipped_count
                )
                if completed % 100 == 0 or completed == self.total_count:
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    logger.info(
                        f"Progress: {completed}/{self.total_count} "
                        f"({completed / self.total_count * 100:.1f}%) "
                        f"- Downloaded: {self.downloaded_count}, "
                        f"Skipped: {self.skipped_count}, "
                        f"Failed: {self.failed_count}, "
                        f"Rate: {rate:.1f} files/sec"
                    )

        # Final summary
        end_time = time.time()
        total_time = end_time - start_time

        logger.info("=" * 60)
        logger.info("DOWNLOAD SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total files: {self.total_count}")
        logger.info(f"Newly downloaded: {self.downloaded_count}")
        logger.info(f"Previously downloaded (skipped): {self.skipped_count}")
        logger.info(f"Failed: {self.failed_count}")
        logger.info(f"Total time: {total_time:.2f} seconds")
        logger.info(f"Average rate: {self.downloaded_count / total_time:.1f} files/sec")

        if self.failed_count > 0:
            logger.warning(f"{self.failed_count} files failed to download")
            return 1
        else:
            logger.info("All files downloaded successfully!")
            return 0


def validate_input_file(file_path: str) -> bool:
    """Validate that the input file exists and is readable"""
    path = Path(file_path)
    if not path.exists():
        logger.error(f"Input file does not exist: {file_path}")
        return False
    if not path.is_file():
        logger.error(f"Input path is not a file: {file_path}")
        return False
    if not os.access(path, os.R_OK):
        logger.error(f"Input file is not readable: {file_path}")
        return False
    return True


def read_file_ids(file_path: str) -> List[str]:
    """Read file IDs from text file with validation"""
    try:
        with open(file_path, "r") as f:
            ids = [line.strip() for line in f if line.strip()]

        if not ids:
            logger.error("No valid IDs found in input file")
            return []

        # Validate ID format (basic check)
        invalid_ids = [
            id for id in ids if not id.replace("-", "").replace("_", "").isalnum()
        ]
        if invalid_ids:
            logger.warning(
                f"Found {len(invalid_ids)} potentially invalid IDs: {invalid_ids[:5]}..."
            )

        logger.info(f"Loaded {len(ids)} file IDs from {file_path}")
        return ids

    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Batch download S3 files using IDs.")
    parser.add_argument("--ids_txt_file", required=True, help="Path to ids.txt")
    parser.add_argument(
        "--aws_path", required=True, help="S3 base path (e.g., s3://bucket/folder)"
    )
    parser.add_argument("--output_path", required=True, help="Local output directory")
    parser.add_argument(
        "--file_extension",
        default="jpg",
        help="File extension to download (default: jpg)",
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=50,
        help="Maximum number of concurrent downloads (default: 50)",
    )
    parser.add_argument(
        "--max_retries",
        type=int,
        default=3,
        help="Maximum number of retry attempts per file (default: 3)",
    )
    parser.add_argument(
        "--log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--log_file",
        default="download.log",
        help="Path to log file (default: download.log)",
    )

    args = parser.parse_args()

    # Setup logging with custom file and level
    global logger
    logger = setup_logging(args.log_file, args.log_level)

    # Validate inputs
    if not validate_input_file(args.ids_txt_file):
        sys.exit(1)

    # Read file IDs
    file_ids = read_file_ids(args.ids_txt_file)
    if not file_ids:
        sys.exit(1)

    # Create download manager and start downloads
    try:
        manager = DownloadManager(
            aws_path=args.aws_path,
            output_path=args.output_path,
            file_extension=args.file_extension,
            max_workers=args.max_workers,
            max_retries=args.max_retries,
        )

        exit_code = manager.download_files(file_ids)
        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
