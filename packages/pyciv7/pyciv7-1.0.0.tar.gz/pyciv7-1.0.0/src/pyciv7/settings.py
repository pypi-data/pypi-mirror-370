import os
from pathlib import Path
import platform
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def default_installation_dir() -> Path:
    system = platform.system()
    if system == "Windows":
        try:
            base = Path(
                os.getenv("LOCALAPPDATA")
                or os.getenv("APPDATA")
                or os.path.join(os.environ["USERPROFILE"], "AppData", "Local")
            )
        except KeyError:
            pass
        else:
            return base / "Firaxis Games" / "Sid Meier's Civilization VII"
    elif system == "Darwin":
        return Path.home() / "Library/Application Support/Civilization VII/"
    elif system == "Linux":
        return Path.home() / "My Games/Sid Meier's Civilization VII/"
    raise FileNotFoundError(
        "Cannot determine the common location of Civilization VII's "
        f"installation on {system}. Manually set this path via "
        "CIV7_INSTALLATION_DIR"
    )


def get_windows_steam_root() -> Optional[Path]:
    import winreg

    key_path = r"SOFTWARE\WOW6432Node\Valve\Steam"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            return Path(winreg.QueryValueEx(key, "InstallPath")[0])
    except FileNotFoundError:
        return None


def guess_posix_steam_root(is_darwin: bool) -> Optional[Path]:
    if is_darwin:
        return Path.home() / "Library/Application Support/Steam"
    else:
        paths = [
            Path.home() / ".steam/steam",
            Path.home() / ".local/share/Steam",
            Path.home()
            / ".var/app/com.valvesoftware.Steam/.local/share/Steam",  # Flatpak
        ]
        for path in paths:
            if path.exists():
                return path


def steam_settings_dir() -> Path:
    system = platform.system()
    if system == "Windows":
        steam_root = get_windows_steam_root()
    else:
        steam_root = guess_posix_steam_root(system == "Darwin")
    if not steam_root:
        raise FileNotFoundError(
            "Cannot determine the common steam location of Civilization VII's "
            f"settings on {system}. Manually set this path via CIV7_SETTINGS_DIR"
        )
    return steam_root / "steamapps/common/Sid Meier's Civilization VII"


def steam_release_bin() -> Path:
    binaries_dir = steam_settings_dir() / "Base" / "Binaries"
    system = platform.system()
    if system == "Windows":
        return binaries_dir / "Win64" / "Civ7_Win64_DX12_FinalRelease.exe"
    else:
        return binaries_dir / system / "Civ7_Win64_Vulkan_FinalRelease"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env", env_file_encoding="utf-8"
    )
    civ7_installation_dir: Path = Field(default_factory=steam_settings_dir)
    civ7_settings_dir: Path = Field(default_factory=default_installation_dir)
    civ7_release_bin: Path = Field(default_factory=steam_release_bin)
