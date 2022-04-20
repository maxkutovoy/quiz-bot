import argparse


def create_parser():
    parser = argparse.ArgumentParser(
        description='Программа переносит вопросы и ответы в базу данных из txt файла')

    parser.add_argument(
        '--path_to_dir',
        help='Путь к каталогу с вопросами',
        nargs='?',
        default='questions',
        type=str,
    )

    parser.add_argument(
        '--encoding',
        help='Кодировка',
        nargs='?',
        default='utf-8',
        type=str,
    )

    return parser
