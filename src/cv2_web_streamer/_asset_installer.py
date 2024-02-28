# https://github.com/dvershinin/lastversion

import platform
import shutil

from pathlib import Path
from lastversion.lastversion import latest, has_update, download_file
from aenum import MultiValueEnum


class Architecture(MultiValueEnum):
    amd64 = "amd64", "x86_64", "AMD64"
    arm64 = "arm64"
    arm64v8 = "arm64v8"
    armv6 = "armv6"
    armv7 = "armv7"


class System(MultiValueEnum):
    darwin = "darwin"
    linux = "linux", "Linux"
    windows = "windows", "Windows"


class AssetInstaller:
    """Allows installation and updating of github released assets"""

    def __init__(
        self,
        repository,
        auto_update=False,
        binary_name=None,
        filter="{system}.*{arch}",
        system_mappings=System,
        arch_mappings=Architecture,
        logger=None,
    ):

        self.logger = logger
        self.filter = filter
        self.repository = repository
        self.system_mappings = system_mappings
        self.arch_mappings = arch_mappings
        self.auto_update = auto_update
        self.repository_name = repository.split("/")[-1]
        self.binary_name = binary_name or self.repository_name

        # Precompute paths
        self.PATH_INSTALL_DIR = (
            Path(__file__).parent.resolve() / f".{self.repository_name}"
        )
        self.PATH_VERSION_FILE = self.PATH_INSTALL_DIR / "version.txt"
        self.PATH_BINARY = self.PATH_INSTALL_DIR / self.binary_name
        self.PATH_ASSET = self.PATH_INSTALL_DIR / "download"

        # Append exe to expected executable path if on windows
        if self._get_system(System) == System.windows:
            self.PATH_BINARY = self.PATH_BINARY.with_suffix(".exe")

    def _get_system(self, mappings=None):
        mappings = mappings or self.system_mappings

        return mappings(platform.system())

    def _get_arch(self, mappings=None):
        mappings = mappings or self.arch_mappings

        return mappings(platform.machine())

    def _get_version_filter(self):
        system = self._get_system().value
        arch = self._get_arch().value

        return self.filter.format(system=system, arch=arch)

    def _log(self, msg):
        if self.logger:
            self.logger.info(msg)
        else:
            print(msg)

    def is_installed(self):
        return self.PATH_BINARY.exists()

    def update(self):
        self._log(f"Checking for updated {self.repository} version")
        current_version = self._get_installed_version()
        latest_version = has_update(self.repository, current_version=current_version)
        if latest_version:
            self._log(
                f"Newer {self.repository} version is available: {current_version} -> {latest_version}"
            )
            self._install_latest_asset()
        else:
            self._log(f"Already on latest {self.repository} version {current_version}")

    def _get_installed_version(self):
        # Version string is cached in VERSION_FILE
        if not self.PATH_VERSION_FILE.exists():
            return "0.0.0"

        with open(self.PATH_VERSION_FILE, "r") as f:
            return f.read()

    def _uninstall_current(self):
        shutil.rmtree(self.PATH_INSTALL_DIR, ignore_errors=True)

    def _get_latest_asset(self):
        filter = self._get_version_filter()
        version = latest(self.repository, output_format="version", assets_filter=filter)
        assets = latest(self.repository, output_format="assets", assets_filter=filter)

        if len(assets) <= 0:
            raise Exception(
                f"Failed to find matching version for this"
                " system/architecture (version filter {filter})"
            )

        filename = Path(assets[0]).name
        return str(version), assets[0], filename

    def _install_latest_asset(self):
        self._log(f"Installing latest {self.repository}")
        self._uninstall_current()

        version, asset, filename = self._get_latest_asset()
        self._log(f"Downloading asset {asset}")

        self.PATH_INSTALL_DIR.mkdir(parents=True)
        self.PATH_VERSION_FILE.write_text(version)

        download_path = self.PATH_INSTALL_DIR / filename

        download_file(asset, download_path.as_posix())

        self._process_download(download_path)

    def _process_download(self, download_path):
        suffix = download_path.suffix
        if suffix == ".gz":
            self._log("Untarring download")
            import tarfile

            tarfile.open(download_path).extractall(self.PATH_INSTALL_DIR)

        elif suffix== ".zip":
            self._log("Unzipping download")
            import zipfile

            with zipfile.ZipFile(download_path, "r") as zip:
                zip.extractall(self.PATH_INSTALL_DIR)

        else:
            # Todo: Case: executable download?
            raise Exception(f"Could not handle extension {suffix} of download {download_path}")

        # Make sure expected binary exists after install
        if not self.is_installed():
            raise Exception(
                f"Could not find binary after processing download! Expected {self.PATH_BINARY.as_posix()} to exist"
            )

    def ensure_install(self, force_update=False):
        if not self.is_installed() or force_update:
            self.update()

    def executable(self):
        self.ensure_install(self.auto_update)

        return self.PATH_BINARY


if __name__ == "__main__":
    installer = AssetInstaller(
        "bluenviron/mediamtx",
        filter="{system}.*{arch}",
    )

    installer.executable()
