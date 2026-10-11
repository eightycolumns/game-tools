from dataclasses import dataclass
from types import SimpleNamespace

@dataclass(frozen=True)
class Subcommand:
    name: str
    description: str

subcommands = SimpleNamespace(
    chess = Subcommand(
        name = 'chess',
        description = 'start a chess study session',
    ),
    go = Subcommand(
        name = 'go',
        description = 'start a go study session',
    ),
    format_pgn = Subcommand(
        name = 'format-pgn',
        description = 'format a PGN problem file',
    ),
    format_sgf = Subcommand(
        name = 'format-sgf',
        description = 'format an SGF problem file',
    ),
)
