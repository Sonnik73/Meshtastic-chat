#!/usr/bin/env python3
"""
Генерирует общий приватный канал (случайный PSK) для команды и сохраняет
его в config/channel.secret.yaml. Запускается ОДИН РАЗ на любом компьютере,
после чего этот же файл используется для настройки обоих (всех) устройств
через provision_device.py, чтобы у всех был одинаковый ключ шифрования.

config/channel.secret.yaml в git не попадает - это ваш секретный ключ,
храните его так же аккуратно, как пароль.
"""
from __future__ import annotations

import base64
import sys

import yaml
from meshtastic.protobuf import apponly_pb2, channel_pb2, config_pb2
from meshtastic.util import genPSK256

from common import CHANNEL_SECRET_PATH, load_team_config


def build_channel_url(psk: bytes, channel_name: str, region: str, modem_preset: str) -> str:
    settings = channel_pb2.ChannelSettings()
    settings.psk = psk
    settings.name = channel_name

    lora_config = config_pb2.Config.LoRaConfig()
    lora_config.region = config_pb2.Config.LoRaConfig.RegionCode.Value(region)
    lora_config.modem_preset = config_pb2.Config.LoRaConfig.ModemPreset.Value(modem_preset)
    lora_config.use_preset = True

    channel_set = apponly_pb2.ChannelSet()
    channel_set.settings.append(settings)
    channel_set.lora_config.CopyFrom(lora_config)

    b64 = base64.urlsafe_b64encode(channel_set.SerializeToString()).decode("ascii").rstrip("=")
    return f"https://meshtastic.org/e/#{b64}"


def main() -> None:
    if CHANNEL_SECRET_PATH.exists():
        sys.exit(
            f"{CHANNEL_SECRET_PATH} уже существует - канал уже сгенерирован.\n"
            "Удалите файл вручную, если действительно хотите выпустить новый ключ "
            "(тогда придётся заново провизионировать ВСЕ устройства)."
        )

    team = load_team_config()
    region = team.get("region", "UNSET")
    modem_preset = team.get("modem_preset", "LONG_FAST")
    channel_name = team.get("channel_name", "team-chat")

    psk = genPSK256()
    url = build_channel_url(psk, channel_name, region, modem_preset)

    CHANNEL_SECRET_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CHANNEL_SECRET_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            {
                "channel_name": channel_name,
                "psk_base64": base64.b64encode(psk).decode("ascii"),
                "channel_url": url,
            },
            f,
            allow_unicode=True,
        )

    print(f"Сохранено в {CHANNEL_SECRET_PATH}\n")
    print("Ссылка приватного канала (одинаковая для всех устройств команды):")
    print(url)
    print(
        "\nЭту ссылку не публикуйте - у кого она есть, тот сможет читать вашу переписку.\n"
        "Дальше запустите provision_device.py для каждого устройства - он применит "
        "этот канал автоматически."
    )

    try:
        import qrcode

        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make()
        print("\nQR-код (можно отсканировать приложением Meshtastic):")
        qr.print_ascii(invert=True)
    except ImportError:
        print(
            "\n(Подсказка: установите пакет 'qrcode' - "
            "pip install qrcode - чтобы здесь же напечатать QR-код."
            " Ссылка выше и так подходит для ручного добавления канала в приложении.)"
        )


if __name__ == "__main__":
    main()
