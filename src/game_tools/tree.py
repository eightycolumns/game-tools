class SgfProblem:
    def __init__(self, path_to_sgf_file):
        with open(path_to_sgf_file, mode='rb') as sgf_file:
            input_bytes = sgf_file.read()

        game = sgf.Sgf_game.from_bytes(input_bytes)
        root_node = game.get_root()
        encoding = root_node.get_encoding()

        self.root_node = root_node

        if root_node.has_property(PropertyIdentifier.VIEW):
            view = root_node.get_raw(PropertyIdentifier.VIEW).decode(encoding)
            return (view == View.FULL_BOARD)
        else:
            return True

    def walk_tree(self):
        stack = [(self.root_node, 0)]

        while stack:
            node, depth = stack.pop()
            yield node, depth

            for child in reversed(node):
                stack.append((child, depth + 1))
