from argparse import ArgumentParser
from textwrap import dedent
from typing import override
import os
import re
import sys

from game_tools import format_pgn, format_sgf, study
from game_tools.config import load_config
from game_tools.logging_config import configure_logging
from game_tools.sgf import Orientation
from game_tools.spaced_repetition import Algorithm
from game_tools.subcommands import subcommands

PROGRAM_NAME = os.path.basename(sys.argv[0])

class Parser(ArgumentParser):
    _active_prog = None

    def __init__(self, *, help_text, **kwargs):
        kwargs.setdefault('allow_abbrev', False)
        kwargs.setdefault('color', False)
        kwargs.setdefault('suggest_on_error', False)
        super().__init__(**kwargs)
        self.help_text = help_text

    @override
    def format_help(self, formatter=None):
        return self.help_text

    @override
    def parse_known_args(self, args=None, namespace=None):
        Parser._active_prog = self.prog
        return super().parse_known_args(args, namespace)

    @override
    def _print_message(self, message, file=None):
        if message and message.startswith(f'{PROGRAM_NAME}:'):
            new_message = message.replace(f'{PROGRAM_NAME}:', f'{Parser._active_prog}:', 1)
            return super()._print_message(new_message, file)
        else:
            return super()._print_message(message, file)

def main():
    usage = f'{PROGRAM_NAME} [-h | --help] [--log-file <log_file>] <subcommand> [<args>]'

    help_text = f'''
        usage: {usage}

        options:
            -h, --help               show this help message and exit
            --log-file <log_file>    path to log file

        subcommands:
            {subcommands.chess.name}         {subcommands.chess.description}
            {subcommands.go.name}            {subcommands.go.description}
            {subcommands.format_pgn.name}    {subcommands.format_pgn.description}
            {subcommands.format_sgf.name}    {subcommands.format_sgf.description}
    '''

    parser = Parser(
        help_text = dedent(help_text).lstrip(),
        prog = PROGRAM_NAME,
        usage = usage,
    )

    parser.add_argument('--log-file')

    subparser_group = parser.add_subparsers(
        dest = 'subcommand',
        metavar = '<subcommand>',
        parser_class = Parser,
        required = True,
    )

    add_study_parser(subparser_group, subcommands.chess)
    add_study_parser(subparser_group, subcommands.go)

    add_format_pgn_parser(subparser_group)
    add_format_sgf_parser(subparser_group)

    args = parser.parse_args()
    configure_logging(args.log_file)

    configurable_subcommands = [subcommands.chess.name, subcommands.go.name]

    if args.subcommand in configurable_subcommands:
        config = load_config(PROGRAM_NAME)
        subcommand_config = config.get(args.subcommand, {})
        args.main(args, subcommand_config)
    else:
        args.main(args)

def add_format_pgn_parser(subparser_group):
    usage = f'{PROGRAM_NAME} {subcommands.format_pgn.name} [-h | --help] <pgn_file>'

    help_text = f'''
        usage: {usage}

        {subcommands.format_pgn.description}

        options:
            -h, --help    show this help message and exit

        positional arguments:
            pgn_file    path to PGN problem file
    '''

    parser = subparser_group.add_parser(
        help_text = dedent(help_text).lstrip(),
        name = subcommands.format_pgn.name,
        prog = f'{PROGRAM_NAME} {subcommands.format_pgn.name}',
        usage = usage,
    )

    parser.add_argument('pgn_file')

    parser.set_defaults(main=format_pgn.main)

def add_format_sgf_parser(subparser_group):
    usage = f'{PROGRAM_NAME} {subcommands.format_sgf.name} [-h | --help] <orientation_option> <sgf_file>'

    help_text = f'''
        usage: {usage}

        {subcommands.format_sgf.description}

        options:
            -h, --help    show this help message and exit

        orientation options:
            --bottom-left-corner     problem is in bottom left corner of board
            --bottom-right-corner    problem is in bottom right corner of board
            --bottom-side            problem is on bottom side of board
            --full-board             problem occupies full board
            --left-side              problem is on left side of board
            --right-side             problem is on right side of board
            --top-left-corner        problem is in top left corner of board
            --top-right-corner       problem is in top right corner of board
            --top-side               problem is on top side of board

        positional arguments:
            sgf_file    path to SGF problem file
    '''

    parser = subparser_group.add_parser(
        help_text = dedent(help_text).lstrip(),
        name = subcommands.format_sgf.name,
        prog = f'{PROGRAM_NAME} {subcommands.format_sgf.name}',
        usage = usage,
    )

    orientation_options = parser.add_mutually_exclusive_group(required=True)

    for orientation in Orientation:
        orientation_options.add_argument(
            '--' + orientation.replace('_', '-'),
            action = 'store_const',
            const = orientation,
            dest = 'orientation',
        )

    parser.add_argument('sgf_file')

    parser.set_defaults(main=format_sgf.main)

def add_study_parser(subparser_group, subcommand):
    usage = f'{PROGRAM_NAME} {subcommand.name} [-h | --help] [--algorithm <algorithm>] [--command <command>] <collection>'

    help_text = f'''
        usage: {usage}

        {subcommand.description}

        options:
            -h, --help                    show this help message and exit
            -a, --algorithm <algorithm>   spaced repetition algorithm (default: fsrs)
            -c, --command <command>       command used to open problem files

        positional arguments:
            collection    path to a collection of problem files
    '''

    parser = subparser_group.add_parser(
        help_text = dedent(help_text).lstrip(),
        name = subcommand.name,
        prog = f'{PROGRAM_NAME} {subcommand.name}',
        usage = usage,
    )

    algorithm_choices = [member.value for member in Algorithm]
    parser.add_argument('-a', '--algorithm', choices=algorithm_choices)
    parser.add_argument('-c', '--command')

    parser.add_argument('collection')

    parser.set_defaults(main=study.main)
