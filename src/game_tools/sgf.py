from enum import StrEnum, auto, unique

@unique
class Orientation(StrEnum):
    BOTTOM_LEFT_CORNER = auto()
    BOTTOM_RIGHT_CORNER = auto()
    BOTTOM_SIDE = auto()
    FULL_BOARD = auto()
    LEFT_SIDE = auto()
    RIGHT_SIDE = auto()
    TOP_LEFT_CORNER = auto()
    TOP_RIGHT_CORNER = auto()
    TOP_SIDE = auto()

@unique
class View(StrEnum):
    BOTTOM_LEFT_CORNER = '[aj:js]',
    BOTTOM_RIGHT_CORNER = '[jj:ss]',
    BOTTOM_SIDE = '[aj:ss]',
    FULL_BOARD = '[aa:ss]',
    LEFT_SIDE = '[aa:js]',
    RIGHT_SIDE = '[ja:ss]',
    TOP_LEFT_CORNER = '[aa:jj]',
    TOP_RIGHT_CORNER = '[ja:sj]',
    TOP_SIDE = '[aa:sj]',

def is_full_board(path_to_problem):
    with open(path_to_problem, mode='rb') as problem:
        input_bytes = problem.read()

    game = sgf.Sgf_game.from_bytes(input_bytes)
    root_node = game.get_root()
    encoding = root_node.get_encoding()

    if root_node.has_property(PropertyIdentifier.VIEW):
        view = root_node.get_raw(PropertyIdentifier.VIEW).decode(encoding)
        return (view == View.FULL_BOARD)
    else:
        return True

def walk_tree(root_node):
    stack = [(root_node, 0)]

    while stack:
        node, depth = stack.pop()
        yield node, depth

        for child in reversed(node):
            stack.append((child, depth + 1))

def create_variant(*, source, destination):
    with TemporaryDirectory as temp_dir:
        path_to_temp_sgf = os.path.join(temp_dir, 'temp.sgf')

        sgftf_option = random.choice([f'-tra{n}' for n in range(8)])
        logging.debug('Randomly selected sgftf option %s', sgftf_option)

        sgftf_command = ['sgftf', sgftf_option, '<', source, '>', path_to_temp_sgf]
        logging.debug('Running command %s', shlex.join(sgftf_command))

        try:
            subprocess.run(
                sgftf_command,
                check = True,
                encoding = 'utf-8',
                errors = 'replace',
                stderr = subprocess.STDOUT,
                stdout = subprocess.PIPE,
            )
        except subprocess.CalledProcessError as e:
            for line in e.output.splitlines():
                logging.error(line)

                logging.exception(
                    '%s failed with exit status %s',
                    shlex.join(sgftf_command),
                    e.returncode,
                )

            fail('Failed to create problem variant')

        if is_full_board(source):
            swap_colors = False
        else:
            swap_colors = random.choice([False, True])

        if swap_colors:
            sgftf_command = ['sgftf', '-swapcolors', '<', path_to_temp_sgf, '>', destination]
            logging.debug('Running command %s', shlex.join(sgftf_command))

            try:
                subprocess.run(
                    sgftf_command,
                    check = True,
                    encoding = 'utf-8',
                    errors = 'replace',
                    stderr = subprocess.STDOUT,
                    stdout = subprocess.PIPE,
                )
            except subprocess.CalledProcessError as e:
                for line in e.output.splitlines():
                    logging.error(line)

                logging.exception(
                    '%s failed with exit status %s',
                    shlex.join(sgftf_command),
                    e.returncode,
                )

                fail('Failed to create problem variant')

            with open(destination, mode='rb') as file:
                input_bytes = file.read()

            game = sgf.Sgf_game.from_bytes(input_bytes)
            root_node = game.get_root()

            for node, depth in walk_tree(root_node):
                pass






            encoding = root_node.get_encoding()

            output_bytes = output.encode(encoding)

            with open(args.sgf_file, mode='wb') as file:
                file.write(output_bytes)



        else:
            shutil.copy(path_to_temp_sgf, destination)
