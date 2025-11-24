"""
Check Updates Use Case
"""
from typing import Optional, Tuple
from packaging import version


class CheckUpdates:
    """Use case for checking for updates from GitHub"""

    def __init__(self, github_updater, current_version: str):
        """
        Initialize the use case

        Args:
            github_updater: GitHub updater service from infrastructure
            current_version: Current version of the application (e.g., '2.1.0')
        """
        self.github_updater = github_updater
        self.current_version = current_version

    def execute(self) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Check for updates from GitHub

        Returns:
            Tuple of (update_available, latest_version, download_url, release_notes)
        """
        try:
            # Get latest release from GitHub
            latest_version, download_url, release_notes = self.github_updater.get_latest_release()

            if not latest_version:
                return False, None, None, None

            # Compare versions
            current = version.parse(self.current_version)
            latest = version.parse(latest_version)

            if latest > current:
                return True, latest_version, download_url, release_notes
            else:
                return False, latest_version, None, None

        except Exception as e:
            print(f"Error checking for updates: {str(e)}")
            return False, None, None, None


class DownloadUpdate:
    """Use case for downloading updates"""

    def __init__(self, github_updater):
        """
        Initialize the use case

        Args:
            github_updater: GitHub updater service from infrastructure
        """
        self.github_updater = github_updater

    def execute(self, download_url: str, output_path: str) -> Tuple[bool, str]:
        """
        Download update from URL

        Args:
            download_url: URL to download the update from
            output_path: Where to save the downloaded file

        Returns:
            Tuple of (success, message)
        """
        try:
            self.github_updater.download_file(download_url, output_path)
            return True, f"Actualización descargada en:\n{output_path}"
        except Exception as e:
            return False, f"Error al descargar actualización: {str(e)}"
