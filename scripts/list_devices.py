#!/usr/bin/env python3
"""
Вспомогательный скрипт: показывает доступные serial-порты и/или сканирует
Bluetooth LE в поисках Meshtastic-устройств поблизости.

Использование:
    python3 scripts/list_devices.py            # список USB serial-портов
    python3 scripts/list_devices.py --ble       # сканирование BLE (~10 сек)
"""
from __future__ import annotations

import argparse


def list_serial_ports() -> None:
    import serial.tools.list_ports

    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("USB serial-порты не найдены. Подключите плату по USB-C.")
        return
    print("Найденные serial-порты:")
    for p in ports:
        print(f"  {p.device}  ({p.description})")


def scan_ble() -> None:
    from meshtastic.ble_interface import BLEInterface

    print("Сканирую BLE (несколько секунд)...")
    devices = BLEInterface.scan()
    if not devices:
        print("Ничего не найдено. Убедитесь, что устройство включено и Bluetooth на компьютере активен.")
        return
    print("Найденные BLE-устройства:")
    for d in devices:
        # elements returned by bleak: объект со свойствами .address / .name (или ble_discovery-обёртка)
        address = getattr(d, "address", d)
        name = getattr(d, "name", "?")
        print(f"  {address}  ({name})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ble", action="store_true", help="сканировать Bluetooth LE вместо serial-портов")
    args = parser.parse_args()

    if args.ble:
        scan_ble()
    else:
        list_serial_ports()


if __name__ == "__main__":
    main()
