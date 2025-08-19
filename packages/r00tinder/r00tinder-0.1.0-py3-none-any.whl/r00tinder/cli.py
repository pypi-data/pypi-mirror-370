import argparse
from .new_device.setup import initialize_new_device
from .reger.reg_start import reger_start


def handle_new_device(args):
    initialize_new_device(args.id, args.model, args.kernel)


def handle_reger(args):
    reger_start(args.id_phone, args.log_level)


def setup_tinder_parser(subparsers):
    # new-device
    parser_new_device = subparsers.add_parser("new-device", help="Инициализация телефона под Tinder")
    parser_new_device.add_argument("--id", type=str.upper, help="Свой идентификатор телефона")
    parser_new_device.add_argument("--model", type=str.upper, help="Модель устройства (например, G950, G955)")
    parser_new_device.add_argument("--kernel", action="store_true", help="Перекомпилировать ядро")
    parser_new_device.set_defaults(func=handle_new_device)

    parser_reger = subparsers.add_parser("reger", help="Зарегистрировать аккаунт в Tinder")
    parser_reger.add_argument("id_phone", type=str, help="ID Device Phone")
    parser_reger.add_argument("--log-level", default='TRACE', type=str, help="Уровень логированния (TRACE, DEBUG, INFO)")
    parser_reger.set_defaults(func=handle_reger)
