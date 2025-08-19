import re
import sys
from pathlib import Path
from r00logger import log
import questionary
from questionary import Style
from collections import defaultdict
from questionary import ValidationError, Validator
from r00arango_connector.tinder import DevicesDB
from r00server import serv

pointer = '-->'
custom_style = Style([
    ('questionmark', 'fg:#673ab7 bold'),  # Фиолетовый жирный знак вопроса
    ('question', 'bold fg:ansicyan'),  # <<< ГОЛУБОЙ ЖИРНЫЙ ТЕКСТ ВОПРОСА
    ('selected', 'fg:#d2da44 bg:'),  # цвет для выбранного элемента
    ('pointer', 'fg:#e0eb16 bold'),  # указатель
    ('answer', 'fg:#e0eb16 bold'),  # жирный ответ после выбора
])


class CountryIsoValidator(Validator):
    """
    Валидатор для ISO-кода страны.
    Проверяет, что код состоит из 2 буквенных символов.
    """
    def validate(self, document):
        text = document.text
        if len(text) != 2:
            raise ValidationError(
                message="ISO-код страны должен состоять ровно из 2 символов.",
                cursor_position=len(text)
            )
        if not text.isalpha(): # Проверяем, что все символы - буквы
            raise ValidationError(
                message="ISO-код страны должен содержать только буквы.",
                cursor_position=len(text)
            )

class CscValidator(Validator):
    """
    Валидатор для CSC-кода.
    Проверяет, что код состоит из 3 буквенных символов.
    """
    def validate(self, document):
        text = document.text
        if len(text) != 3:
            raise ValidationError(
                message="CSC код должен состоять ровно из 3 символов.",
                cursor_position=len(text)
            )
        if not text.isalpha(): # Проверяем, что все символы - буквы
            raise ValidationError(
                message="CSC код должен содержать только буквы.",
                cursor_position=len(text)
            )


class ProxyValidator(Validator):
    """
    Валидатор для проверки формата IP:PORT.
    Поддерживает IPv4 и порты от 1 до 65535.
    """
    # Регулярное выражение для проверки IP:PORT (простой случай IPv4)
    # Более строгое regex для IP: ^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$
    # Но для удобства можно использовать упрощенный вариант и проверять части
    IP_PORT_REGEX = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$")

    def validate(self, document):
        proxy_str = document.text
        if not self.IP_PORT_REGEX.match(proxy_str):
            raise ValidationError(
                message="Неверный формат. Ожидается IP:PORT (например, 192.168.1.1:8080).",
                cursor_position=len(proxy_str)
            )

        # Дополнительная проверка на валидность IP-адреса и порта
        parts = proxy_str.split(':')
        if len(parts) != 2: # Это уже должно быть отловлено regex, но для надежности
            raise ValidationError(
                message="Неверный формат. Ожидается IP:PORT.",
                cursor_position=len(proxy_str)
            )

        ip_part, port_part = parts[0], parts[1]

        # Проверка IP-адреса
        ip_octets = ip_part.split('.')
        if len(ip_octets) != 4:
            raise ValidationError(
                message="Неверный IP-адрес. Должен быть в формате IPv4 (например, 192.168.1.1).",
                cursor_position=len(ip_part)
            )
        for octet in ip_octets:
            try:
                num = int(octet)
                if not (0 <= num <= 255):
                    raise ValidationError(
                        message=f"Неверный октет IP-адреса: {octet}. Значение должно быть от 0 до 255.",
                        cursor_position=len(proxy_str)
                    )
            except ValueError:
                raise ValidationError(
                    message="Неверный IP-адрес. Октет должен быть числом.",
                    cursor_position=len(proxy_str)
                )

        # Проверка порта
        try:
            port = int(port_part)
            if not (1 <= port <= 65535):
                raise ValidationError(
                    message="Неверный порт. Порт должен быть в диапазоне от 1 до 65535.",
                    cursor_position=len(proxy_str)
                )
        except ValueError:
            raise ValidationError(
                message="Неверный порт. Порт должен быть числом.",
                cursor_position=len(proxy_str)
            )


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text) # Пытаемся преобразовать в целое число
        except ValueError:
            raise ValidationError(
                message="Пожалуйста, введите корректное целое число.",
                cursor_position=len(document.text)) # Устанавливаем курсор в конец поля



class MenuTui:
    @staticmethod
    def is_recovery():
        answer = questionary.select(
            "Прошить recovery ?",
            choices=[
                questionary.Choice(title="Да", value=True),
                questionary.Choice(title="Нет", value=False),
            ],
            pointer=pointer,
            style=custom_style
        ).ask()
        if isinstance(answer, bool):
            return answer
        sys.exit(-1)

    @staticmethod
    def ask_firmware_name(firmware_root_dir: Path) -> Path:
        firmware_names = [filepath.name for filepath in firmware_root_dir.glob('source*')]
        answer = questionary.select(
            "Имя прошивки?",
            choices=firmware_names,
            pointer=pointer,
            style=custom_style
        ).ask()

        if str(answer).startswith('source'):
            firmware_dir = firmware_root_dir / answer
            return Path(firmware_dir)
        sys.exit(-1)

    @staticmethod
    def ask_country_iso():
        answer = questionary.text(
            "Введи ISO-код страны (например, RU, US, GB):",
            style=custom_style,
            validate=CountryIsoValidator(),
        ).ask()

        if answer is not None:
            return answer
        sys.exit(-1)


    @staticmethod
    def ask_spath_magisk_zip():
        answer = questionary.text(
            "Введи magisk.zip путь (на сервере)",
            style=custom_style,
            default='zip/magisk_context.zip'
        ).ask()

        if answer is not None:
            return answer
        sys.exit(-1)

    @staticmethod
    def ask_device_server():
        servers = ['server0', 'server1']
        answer = questionary.select(
            "Выбери сервер где будут запускаться скрипты для девайса",
            style=custom_style,
            choices=servers,
        ).ask()

        if answer:
            return answer
        sys.exit(-1)

    @staticmethod
    def ask_proxy_server():
        servers = ['server0', 'server1']
        answer = questionary.select(
            "Выбери сервер где будет проксификация девайса",
            style=custom_style,
            choices=servers,
        ).ask()

        if answer:
            return answer
        sys.exit(-1)

    @staticmethod
    def ask_proxy_service():
        servers = [Path(item).name for item in serv.list('proxy')]
        answer = questionary.select(
            "Выбери прокси сервис",
            style=custom_style,
            choices=servers,
        ).ask()

        if answer:
            return answer
        sys.exit(-1)


