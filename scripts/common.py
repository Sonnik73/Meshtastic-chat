"""Общие функции для скриптов настройки Meshtastic-устройств."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"
TEAM_CONFIG_PATH = CONFIG_DIR / "team.yaml"
CHANNEL_SECRET_PATH = CONFIG_DIR / "channel.secret.yaml"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        sys.exit(
            f"Файл {path} не найден.\n"
            f"Скопируйте {path.with_suffix('')}.example.yaml -> {path.name} "
            f"(или запустите generate_channel.py, если речь о секрете канала)."
        )
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_team_config() -> dict:
    return load_yaml(TEAM_CONFIG_PATH)


def load_channel_secret() -> dict:
    return load_yaml(CHANNEL_SECRET_PATH)


def add_connection_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--port",
        help="Serial-порт устройства (например /dev/ttyUSB0 или COM5). "
        "Используйте для первичной настройки по USB.",
    )
    group.add_argument(
        "--ble",
        metavar="ADDRESS_OR_NAME",
        help="MAC-адрес или имя BLE-устройства (см. list_devices.py --ble). "
        "Используйте, если платы уже спарены по Bluetooth.",
    )


def open_interface(args: argparse.Namespace):
    """Открывает соединение с устройством по serial или BLE в зависимости от args."""
    if args.port:
        from meshtastic.serial_interface import SerialInterface

        print(f"Подключаюсь по USB: {args.port} ...")
        return SerialInterface(devPath=args.port)

    from meshtastic.ble_interface import BLEInterface

    print(f"Подключаюсь по BLE: {args.ble} ...")
    return BLEInterface(address=args.ble)
