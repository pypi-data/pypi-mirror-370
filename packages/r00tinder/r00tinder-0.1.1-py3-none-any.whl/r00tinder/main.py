import argparse
from r00logger import log
from .cli import setup_tinder_parser


def create_parser():
    parser = argparse.ArgumentParser(
        description="Инструмент для работы с прошивками и ядрами Android",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True, title="Основные команды")
    setup_tinder_parser(subparsers)
    return parser


@log.catch
def main():
    parser = create_parser()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()