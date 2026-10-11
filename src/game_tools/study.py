from enum import StrEnum, unique
from tempfile import TemporaryDirectory
import datetime as dt
import logging

from sgfmill import sgf

from game_tools.logging_config import configure_logging
from game_tools.spaced_repetition import Algorithm, DEFAULT_ALGORITHM
from game_tools.subcommands import subcommands
from game_tools.util import fail

WEIGHT_PRECISION = 2
MIN_WEIGHT = 1 / 10 ** WEIGHT_PRECISION

@unique
class FilenameExtension(StrEnum):
    PGN = '.pgn'
    SGF = '.sgf'

def main(args, config):
    logger = logging.getLogger(__name__)

    algorithm = args.algorithm or config.get('algorithm') or DEFAULT_ALGORITHM
    logger.debug('Algorithm set to %s', algorithm)

    command = args.command or config.get('command')

    if command:
        logger.debug('Command set to %s', command)
    else:
        fail('Command not set')

#   if not os.path.isdir(args.collection):
#       fail(f'Error: Collection {args.path_to_collection_dir} not found')

#   path_to_state_dir = os.path.join(args.collection, '.state', algorithm)
#   os.makedirs(path_to_state_dir, exist_ok=True)

#   path_to_state_config_file = os.path.join(path_to_state_dir, 'config.json')

#   if os.path.isfile(path_to_state_config_file):
#       with open(path_to_state_config_file, encoding='utf-8', mode='r') as state_config_file:
#           state_config = json.load(state_config_file)
#   else:
#       state_config = {'cards': {}}

#   cards = state_config['cards']
#   orphaned_cards = []

#   for problem in cards:
#       path_to_problem = os.path.join(args.collection, problem)

#       if not os.path.isfile(path_to_problem):
#           orphaned_cards.append(problem)

#   if orphaned_cards:
#       fail(f'Error: Orphaned cards: {", ".join(sorted(orphaned_cards))}')

#   file_extension = {
#       subcommands.chess.name: FilenameExtension.PGN,
#       subcommands.go.name: FilenameExtension.SGF,
#   }[subcommand.name]

#   all_problems = [
#       problem for problem in os.listdir(args.collection)
#       if os.path.isfile(os.path.join(args.collection, problem))
#       and problem.endswith(file_extension)
#   ]

#   if not all_problems:
#       fail(f'Error: No problem files in collection {args.collection}')

#   for problem in all_problems:
#       if problem not in cards:
#           cards[problem] = create_card(args.algorithm)

#   now = dt.datetime.now(dt.timezone.utc)

#   past_due_problems = [
#       problem for problem in all_problems
#       if cards[problem].due < now
#   ]
#   selectable_problems = past_due_problems

#   weights = [
#       calculate_weight(scheduler, cards[problem], now)
#       for problem in past_due_problems
#   ]

#   scheduler = create_scheduler(args.algorithm)
#   review_logs = []

#   with TemporaryDirectory as temp_dir:
#       while True:
#           if not selectable_problems:
#               selectable_problems = all_problems.copy()

#               weights = [
#                   calculate_weight(scheduler, cards[problem], now)
#                   for problem in all_problems
#               ]

#           problem = random.choices(selectable_problems, weights)[0]
#           print(f'Selected {problem}')

#           path_to_problem = os.path.join(args.collection, problem)

#           if path_to_problem.endswith(FilenameExtension.SGF):
#               path_to_problem_variant = os.path.join(temp_dir, problem)
#               create_variant(source=path_to_problem, destination=path_to_problem_variant)





#               if not is_full_board(path_to_problem):
#                   swap_colors(source=path_to_problem_variant, destination=path_to_problem_variant)

#               with open(path_to_problem, mode='rb') as problem:
#                   input_bytes = problem.read()

#               game = sgf.Sgf_game.from_bytes(input_bytes)
#               root_node = game.get_root()
#               encoding = root_node.get_encoding()

#               if root_node.has_property(PropertyIdentifier.VIEW):
#                   view_property_value = root_node.get_raw(PropertyIdentifier.VIEW).decode(encoding)
#                   swap_colors = (view_property_value != View.FULL_BOARD)
#               else:
#                   swap_colors = False

#               path_to_problem_variant = os.path.join(temp_dir, problem)

#               if swap_colors:
#                   try:
#                       subprocess.run(
#                           ['sgftf', '-swapcolors', '<', path_to_temp_sgf, '>', path_to_problem_variant],
#                           check = True,
#                           encoding = 'utf-8',
#                           errors = 'replace',
#                           stderr = subprocess.STDOUT,
#                           stdout = subprocess.PIPE,
#                       )
#                   except subprocess.CalledProcessError as e:
#                       print_stderr(e.output)
#                       fail(f'Error: Command had exit status {e.returncode}')

#                   os.remove(path_to_temp_sgf)

#                   # TODO: Swap colors in comments
#                   with open(path_to_problem_variant, mode='rb') as file:
#                       input_bytes = file.read()
#               else:
#                   os.rename(path_to_temp_sgf, path_to_problem_variant)





#           try:
#               subprocess.run(
#                   [*shlex.split(command), path_to_problem_variant],
#                   check = True,
#                   encoding = 'utf-8',
#                   errors = 'replace',
#                   stderr = subprocess.STDOUT,
#                   stdout = subprocess.PIPE,
#               )
#           except subprocess.CalledProcessError as e:
#               print_stderr(e.output)
#               fail(f'Error: Command had exit status code {e.returncode}')

#           response = None

#       while not is_yes_or_no(response):
#           response = input('Success? (y/n) ')

#       reviewed_card, review_log = review_card(scheduler, cards[problem], response)

#       cards[problem] = reviewed_card
#       review_logs.append(review_log)

#       index_of_selected_problem = selectable_problems.index(problem)
#       del selectable_problems[index_of_selected_problem]
#       del weights[index_of_selected_problem]

#       response = None

#       while not is_yes_or_no(response):
#           response = input('Another? (y/n) ')

#       if is_no(response):
#           break

def calculate_weight(scheduler, card, now):
    if isinstance(scheduler, fsrs.Scheduler):
        retrievability = scheduler.get_card_retrievability(card, now)
        weight = 1 - retrievability
    else:
        raise TypeError(f'Unsupported scheduler class: {type(scheduler)}')

    weight = round(weight, WEIGHT_PRECISION)

    return max(weight, MIN_WEIGHT)

def create_card(algorithm):
    if algorithm == Algorithm.FSRS:
        return fsrs.Card()

    raise ValueError(f'Unsupported algorithm: {algorithm}')

def create_scheduler(algorithm):
    if algorithm == Algorithm.FSRS:
        return fsrs.Scheduler(learning_steps=(), relearning_steps=(), maximum_interval=365)

    raise ValueError(f'Unsupported algorithm: {algorithm}')

def is_no(response):
    return isinstance(response, str) and response.lower() in ['n', 'no']

def is_yes(response):
    return isinstance(response, str) and response.lower() in ['y', 'yes']

def is_yes_or_no(response):
    return is_yes(response) or is_no(response)

# TODO: Add --logging and --no-logging options, defaulting to no logging
# TODO: Add --variants and --no-variants options, defaulting to variants
