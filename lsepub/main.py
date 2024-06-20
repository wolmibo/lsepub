# Copyright (c) 2024 wolmibo
# SPDX-License-Identifier: MIT

import argparse
from pathlib import Path
import sys

from lsepub.book import Book
import lsepub.meta as META


def list_directory(path, args):
    books = []

    for child in path.iterdir():
        if child.is_file():
            books += list_file(child, args)
        elif child.is_dir() and args.recursive:
            books += list_directory(child, args)

    return books


def list_file(path, args):
    if path.is_file():
        book = Book(path)
        if book.is_epub():
            return [book]

    return []


def use_color(args):
    return (args.color == 'always' or
            (args.color == 'auto' and sys.stdout.isatty()))


def dim(text, args):
    if use_color(args):
        return f'\033[2m{text}\033[0m'
    return text


def bold(text, args):
    if use_color(args):
        return f'\033[1m{text}\033[0m'
    return text


def creators(book, args):
    if book.creators() == []:
        return ''

    creators = ', '.join(book.creators())
    return bold(creators, args) + ' \\\\ '


def fill(text, width):
    return text + ' ' * max(width - len(text), 0)


def print_books_short(books, args):
    for book in books:
        print((f'{dim(book.path(), args)}: '
               f'{creators(book, args)}{book.title()}'))


def print_books_long(books, args):
    for book in books:
        print(f'{creators(book, args)}{book.title()}')
        print(f'  {dim("Path:     ", args)}{book.path()}')

        if not book.language() is None:
            print(f'  {dim("Language: ", args)}{book.language()}')

        if book.subjects() != []:
            print(f'  {dim("Subjects: ", args)}{", ".join(book.subjects())}')

        print('')


def print_books_tabular(books, args):
    paths = [str(book.path()) for book in books]
    creators = [', '.join(book.creators()) for book in books]
    titles = [book.title() for book in books]

    pathswidth = max([len(path) for path in paths])
    creatorswidth = max([len(creator) for creator in creators])

    for (path, creator, title) in zip(paths, creators, titles):
        print((f'{dim(fill(path, pathswidth), args)}  '
               f'{bold(fill(creator, creatorswidth), args)}  '
               f'{title}'))


def print_books(books, args):
    if args.format == 'tabular':
        print_books_tabular(books, args)
    elif args.format == 'long':
        print_books_long(books, args)
    else:
        print_books_short(books, args)


def print_version():
    print(f'{META.name} {META.version}')
    exit(0)


def main():
    parser = argparse.ArgumentParser(description=META.description)

    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='show version information and exit')

    parser.add_argument('path',
                        metavar='PATH',
                        nargs='*',
                        type=Path,
                        help='Files or directories to inspect')

    parser.add_argument('-r', '--recursive',
                        action='store_true',
                        help='List directories recursively')

    parser.add_argument('-c', '--color',
                        metavar='WHEN',
                        choices=['always', 'auto', 'never'],
                        default='auto',
                        help=('When to use terminal colors '
                              '(always, auto, never)'))

    parser.add_argument('-f', '--format',
                        metavar='FORMAT',
                        choices=['short', 's', 'long', 'l', 'tabular', 't'],
                        default='short',
                        help=('Which output format to use '
                              '(s[hort], l[ong], t[abular])'))

    parser.add_argument('-l', '--long',
                        action='store_true',
                        help='Use longformat output')
    parser.add_argument('-t', '--tabular',
                        action='store_true',
                        help='Use tabular output')
    parser.add_argument('-s', '--short',
                        action='store_true',
                        help='Use short output')

    args = parser.parse_args()

    if args.version:
        print_version()

    if args.format == 's' or args.short:
        args.format = 'short'
    elif args.format == 'l' or args.long:
        args.format = 'long'
    elif args.format == 't' or args.tabular:
        args.format = 'tabular'

    paths = args.path
    if paths == []:
        paths = [Path('.')]

    books = []
    for path in paths:
        if path.is_file():
            books += list_file(path, args)
        elif path.is_dir():
            books += list_directory(path, args)

    print_books(books, args)
