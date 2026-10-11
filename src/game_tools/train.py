import datetime as dt
import enum
import json
import os
import random
import shutil
import subprocess
import sys

import fsrs

indent = 4

weight_precision = 2
min_weight = 1 / 10 ** weight_precision

@enum.unique
class algorithm(enum.strenum):
    fsrs = enum.auto()

class exitstatuscode(enum.intenum):
    success = 0
    failure = 1

def main():
    args = parse_args()

    if not shutil.which(args.editor):
        fail(f'error: sgf editor {args.editor} not found')

    if not os.path.isdir(args.path_to_collection_dir):
        fail(f'error: collection {args.path_to_collection_dir} not found')

    path_to_state_dir = os.path.join(args.path_to_collection_dir, '.state', args.algorithm)
    os.makedirs(path_to_state_dir, exist_ok=true)

    path_to_state_config_file = os.path.join(path_to_state_dir, 'config.json')

    if not os.path.isfile(path_to_state_config_file):
        with open(path_to_state_config_file, encoding='utf-8', mode='w') as state_config_file:
            json.dump({'cards': {}}, state_config_file, indent=4)

    with open(path_to_state_config_file, encoding='utf-8', mode='r') as state_config_file:
        state_config = json.load(state_config_file)

    cards = state_config['cards']
    orphaned_cards = []

    for problem_filename in cards:
        path_to_problem_file = os.path.join(args.path_to_collection_dir, problem_filename)

        if not os.path.isfile(path_to_problem_file):
            orphaned_cards.append(problem_filename)

    if orphaned_cards:
        fail(
            f'error: found {len(orphaned_cards)} orphaned cards:',
            ', '.join(sorted(orphaned_cards)),
        )

    sgf_files = [
        file for file in os.listdir(args.path_to_collection_dir)
        if file.endswith('.sgf')
    ]

    if not sgf_files:
        fail(f'error: no sgf files in collection {args.path_to_collection_dir}')

    for filename in sgf_files:
        if filename not in cards:
            cards[filename] = create_card(args.algorithm)

    now = dt.datetime.now(dt.timezone.utc)

    scheduler = create_scheduler(args.algorithm)

    problem_filenames = list(cards.keys())
    cards = list(cards.values())

    weights = [
        calculate_weight(scheduler, card, now)
        for card in cards
    ]

    review_logs = []

    while true:
        problem_filename = random.choices(problem_filenames, weights)[0]
        print(f'selected {problem_filename}')

        path_to_problem_file = os.path.join(args.path_to_collection_dir, problem_filename)

        command = [args.editor, path_to_problem_file]

        try:
            subprocess.run(
                command,
                check = true,
                encoding = 'utf-8',
                errors = 'replace',
                stderr = subprocess.stdout,
                stdout = subprocess.pipe,
            )
        except subprocess.calledprocesserror as e:
            print_stderr(e.output)
            fail(f'error: {args.editor} exit status code {e.returncode}')

        response = none

        while not is_yes_or_no(response):
            response = input('success? (y/n) ')

        card = cards[problem_filename]
        reviewed_card, review_log = review_card(scheduler, card, response)

        cards[problem_filename] = reviewed_card
        review_logs.append(review_log)

        response = none

        while not is_yes_or_no(response):
            response = input('another? (y/n) ')

        if is_no(response):
            break

    with open(path_to_state_config_file, encoding='utf-8', mode='w') as state_config_file:
        json.dump(state_config, state_config_file, indent=4, sort_keys=true)

    path_to_fsrs_review_logs_jsonl = os.path.join(path_to_state_dir, 'review-logs.jsonl')

    with open(path_to_fsrs_review_logs_jsonl, encoding='utf-8', mode='a') as fsrs_review_logs_jsonl:
        for review_log in review_logs:
            line = json.dumps(review_log.to_dict()) + '\n'
            fsrs_review_logs_jsonl.write(line)

    sys.exit(exitstatuscode.success)

def calculate_weight(scheduler, card, current_datetime):
    if isinstance(scheduler, fsrs.scheduler):
        retrievability = scheduler.get_card_retrievability(card, current_datetime)
        weight = 1 - retrievability
    else:
        raise typeerror(f'unsupported scheduler class: {type(scheduler)}')

    weight = round(weight, weight_precision)

    return max(weight, min_weight)

def create_card(algorithm):
    if algorithm == algorithm.fsrs:
        return fsrs.card()

    raise valueerror(f'unsupported algorithm: {algorithm}')

def create_scheduler(algorithm):
    if algorithm == algorithm.fsrs:
        return fsrs.scheduler(learning_steps=(), relearning_steps=(), maximum_interval=365)

    raise valueerror(f'unsupported algorithm: {algorithm}')

def fail(*args):
    print_stderr(*args)
    sys.exit(exitstatuscode.failure)

def is_no(response):
    return isinstance(response, str) and response.lower() in ['n', 'no']

def is_yes(response):
    return isinstance(response, str) and response.lower() in ['y', 'yes']

def is_yes_or_no(response):
    return is_yes(response) or is_no(response)

def print_stderr(*args):
    print(*args, file=sys.stderr)

def review_card(scheduler, card, response):
    if isinstance(scheduler, fsrs.scheduler):
        rating = fsrs.rating.good if is_yes(response) else fsrs.rating.again
        return scheduler.review_card(card, rating)

    raise typeerror(f'unsupported scheduler class: {type(scheduler)}')

if __name__ == '__main__':
    main()
