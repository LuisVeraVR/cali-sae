"""
GitHub Updater - Checks and downloads updates from GitHub releases
"""
import requests
from typing import Tuple, Optional
from pathlib import Path


class GitHubUpdater:
    """Handles checking and downloading updates from GitHub releases"""

    def __init__(
        self,
        repo_owner: str = "LuisVeraVR",
        repo_name: str = "cali-sae",
        timeout: int = 5
    ):
        """
        Initialize GitHub updater

        Args:
            repo_owner: GitHub repository owner
            repo_name: GitHub repository name
            timeout: Request timeout in seconds
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.timeout = timeout
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    def get_latest_release(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Get latest release information from GitHub

        Returns:
            Tuple of (version, download_url, release_notes)
            Returns (None, None, None) if unable to fetch
        """
        try:
            response = requests.get(self.api_url, timeout=self.timeout)

            if response.status_code == 200:
                release_data = response.json()

                # Extract version (remove 'v' prefix if present)
                version = release_data.get("tag_name", "").replace("v", "")

                # Extract download URL from assets
                assets = release_data.get("assets", [])
                download_url = None

                if assets:
                    # Look for .exe file first
                    for asset in assets:
                        if asset.get("name", "").endswith(".exe"):
                            download_url = asset.get("browser_download_url")
                            break

                    # If no .exe, use first asset
                    if not download_url and assets:
                        download_url = assets[0].get("browser_download_url")

                # Extract release notes
                release_notes = release_data.get("body", "No hay notas de versión disponibles")

                return version, download_url, release_notes

        except requests.exceptions.Timeout:
            print("Timeout al verificar actualizaciones")
        except requests.exceptions.ConnectionError:
            print("Error de conexión al verificar actualizaciones")
        except Exception as e:
            print(f"Error al verificar actualizaciones: {str(e)}")

        return None, None, None

    def download_file(self, url: str, output_path: str, chunk_size: int = 8192) -> None:
        """
        Download a file from URL

        Args:
            url: URL to download from
            output_path: Where to save the file
            chunk_size: Size of chunks to download (bytes)

        Raises:
            Exception if download fails
        """
        try:
            # Create output directory if it doesn't exist
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            # Download file with streaming
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(output_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error descargando archivo: {str(e)}")
        except IOError as e:
            raise Exception(f"Error guardando archivo: {str(e)}")

    def get_download_size(self, url: str) -> Optional[int]:
        """
        Get the size of a file to download

        Args:
            url: URL to check

        Returns:
            Size in bytes or None if unable to determine
        """
        try:
            response = requests.head(url, timeout=self.timeout)
            if response.status_code == 200:
                content_length = response.headers.get('Content-Length')
                if content_length:
                    return int(content_length)
        except Exception:
            pass

        return None
