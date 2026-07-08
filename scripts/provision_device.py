#!/usr/bin/env python3
"""
Настраивает одно Meshtastic-устройство: применяет общий приватный канал
команды (из config/channel.secret.yaml), роль узла и имя владельца
(из config/team.yaml).

Примеры:
    python3 scripts/provision_device.py --device alice --port /dev/ttyUSB0
    python3 scripts/provision_device.py --device bob --ble AA:BB:CC:DD:EE:FF

Сначала настройте оба устройства по USB (--port) - это надёжнее всего для
первого запуска. Для повторной настройки уже спаренного по Bluetooth
устройства можно использовать --ble.
"""
from __future__ import annotations

import argparse
import sys
import time

from meshtastic.protobuf import config_pb2

from common import add_connection_args, load_channel_secret, load_team_config, open_interface


def find_device_entry(team: dict, device_id: str) -> dict:
    for dev in team.get("devices", []):
        if dev.get("id") == device_id:
            return dev
    sys.exit(
        f"Устройство с id='{device_id}' не найдено в config/team.yaml (devices).\n"
        "Добавьте его туда или проверьте написание --device."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--device", required=True, help="id устройства из config/team.yaml, например alice"
    )
    add_connection_args(parser)
    args = parser.parse_args()

    team = load_team_config()
    channel = load_channel_secret()
    dev = find_device_entry(team, args.device)
    role_name = team.get("role", "CLIENT")

    iface = open_interface(args)
    try:
        print("Жду начальную конфигурацию узла...")
        iface.waitForConfig()
        node = iface.localNode

        print(f"Устанавливаю имя узла: {dev['long_name']} / {dev['short_name']}")
        node.setOwner(dev["long_name"], dev["short_name"])

        print(f"Применяю приватный канал команды '{channel['channel_name']}'...")
        node.setURL(channel["channel_url"])

        print(f"Устанавливаю роль узла: {role_name}")
        node.localConfig.device.role = config_pb2.Config.DeviceConfig.Role.Value(role_name)
        node.writeConfig("device")

        print("Перезагружаю устройство для применения настроек...")
        node.reboot()
        time.sleep(2)
    finally:
        iface.close()

    print(f"\nГотово: устройство '{args.device}' настроено и перезагружается.")
    print(
        "Дальше на телефоне: приложение Meshtastic -> Bluetooth -> найдите устройство "
        f"'{dev['short_name']}' / '{dev['long_name']}' и подключитесь."
    )


if __name__ == "__main__":
    main()
