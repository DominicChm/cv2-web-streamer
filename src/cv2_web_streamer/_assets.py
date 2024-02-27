from aenum import MultiValueEnum

from ._asset_installer import AssetInstaller


class MTXArchMappings(MultiValueEnum):
    amd64 = "amd64", "x86_64", "AMD64"
    arm64 = "arm64", "aarch64"
    arm64v8 = "arm64v8"
    armv6 = "armv6"
    armv7 = "armv7"


class MTXSystemMappings(MultiValueEnum):
    darwin = "darwin"
    linux = "linux", "Linux"
    windows = "windows", "Windows"


class FFMpegArchMappings(MultiValueEnum):
    amd64 = "64", "amd64", "x86_64", "AMD64"
    arm64 = "arm-64", "arm64", "arm64v8", "aarch64"


class FFMpegSystemMappings(MultiValueEnum):
    darwin = "darwin"
    linux = "linux", "Linux"
    windows = "win", "windows", "Windows"


# Asset installers
mediamtx = AssetInstaller(
    "bluenviron/mediamtx",
    filter="{system}.*{arch}",
    arch_mappings=MTXArchMappings,
    system_mappings=MTXSystemMappings,
)

ffmpeg = AssetInstaller(
    "ffbinaries/ffbinaries-prebuilt",
    filter="ffmpeg.*{system}.*{arch}",
    arch_mappings=FFMpegArchMappings,
    system_mappings=FFMpegSystemMappings,
    binary_name="ffmpeg",
)


def ensure_assets_installed():
    mediamtx.ensure_install()
    ffmpeg.ensure_install()

if __name__ == "__main__":
    ensure_assets_installed()