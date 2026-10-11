from enum import StrEnum, unique

from sgfmill import sgf

from game_tools.util import fail

def main(args):
    print(f'Formatting {args.sgf_file}')

    try:
        with open(args.sgf_file, mode='rb') as file:
            input_bytes = file.read()

        game = sgf.Sgf_game.from_bytes(input_bytes)
        root_node = game.get_root()

        output = '(\n'
        output += _format_root_node(root_node, args.orientation)
        output += ')\n'

        encoding = root_node.get_encoding()
        output_bytes = output.encode(encoding)

        with open(args.sgf_file, mode='wb') as file:
            file.write(output_bytes)
    except FileNotFoundError:
        fail(f'Error: {args.sgf_file} file not found')

_INDENT = 4 * ' '

@unique
class _PropertyIdentifier(StrEnum):
    ADD_BLACK = 'AB'
    ADD_WHITE = 'AW'
    BOARD_SIZE = 'SZ'
    CHARSET = 'CA'
    COMMENT = 'C'
    FILE_FORMAT = 'FF'
    GAME_TYPE = 'GM'
    PLAYER = 'PL'
    VIEW = 'VW'

def _format_child_nodes(node, indent):
    child_nodes = list(node)

    if len(child_nodes) == 1:
        result = _format_node(child_nodes[0], indent=indent)
    else:
        result = ''

        for child_node in child_nodes:
            result += indent + '(\n'
            result += _format_node(child_node, indent=indent+_INDENT)
            result += indent + ')\n'

    return result

def _format_node(node, indent):
    result = indent + ';'

    for property_identifier in node.properties():
        result += _format_property(node, property_identifier)

    result += '\n'

    result += _format_child_nodes(node, indent)

    return result

def _format_property(node, property_identifier):
    encoding = node.get_encoding()
    property_values = node.get_raw_list(property_identifier)
    property_values_decoded = [value.decode(encoding) for value in property_values]

    if property_identifier in [_PropertyIdentifier.ADD_BLACK, _PropertyIdentifier.ADD_WHITE]:
        property_values_decoded.sort()

    property_values_formatted = ''.join([f'[{value}]' for value in property_values_decoded])

    return property_identifier + property_values_formatted

def _format_root_node(node, orientation):
    supported_properties = [
        _PropertyIdentifier.FILE_FORMAT,
        _PropertyIdentifier.CHARSET,
        _PropertyIdentifier.GAME_TYPE,
        _PropertyIdentifier.BOARD_SIZE,
        _PropertyIdentifier.VIEW,
        _PropertyIdentifier.ADD_BLACK,
        _PropertyIdentifier.ADD_WHITE,
        _PropertyIdentifier.PLAYER,
        _PropertyIdentifier.COMMENT,
    ]

    _prune_root_node(node, supported_properties)

    result = _INDENT + ';'

    for property_identifier in supported_properties:
        if property_identifier == _PropertyIdentifier.VIEW:
            result += _format_view(orientation)
        elif node.has_property(property_identifier):
            result += _format_property(node, property_identifier)

    result += '\n'

    result += _format_child_nodes(node, _INDENT)

    return result

def _format_view(orientation):
    view_property_values = {
        SgfProblemOrientation.BOTTOM_LEFT_CORNER: '[aj:js]',
        SgfProblemOrientation.BOTTOM_RIGHT_CORNER: '[jj:ss]',
        SgfProblemOrientation.BOTTOM_SIDE: '[aj:ss]',
        SgfProblemOrientation.FULL_BOARD: '[aa:ss]',
        SgfProblemOrientation.LEFT_SIDE: '[aa:js]',
        SgfProblemOrientation.RIGHT_SIDE: '[ja:ss]',
        SgfProblemOrientation.TOP_LEFT_CORNER: '[aa:jj]',
        SgfProblemOrientation.TOP_RIGHT_CORNER: '[ja:sj]',
        SgfProblemOrientation.TOP_SIDE: '[aa:sj]',
    }

    return _PropertyIdentifier.VIEW + view_property_values[orientation]

def _prune_root_node(node, supported_properties):
    discarded_properties = []

    for property_identifier in node.properties():
        if property_identifier not in supported_properties:
            node.unset(property_identifier)
            discarded_properties.append(property_identifier)

    if discarded_properties:
        print(
            'Discarded root node properties:',
            ', '.join(sorted(discarded_properties)),
        )
