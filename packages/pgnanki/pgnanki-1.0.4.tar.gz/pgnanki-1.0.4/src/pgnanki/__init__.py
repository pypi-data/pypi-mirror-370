"""Making Anki notes of type Chess 2.0 for one color's positions in a PGN.

Classes
-------
ShortStringExporter
    A subclass of StringExporter for one paragraph and no non-FEN headers.

Functions
---------
traverse_trans
    Traverse descendants of a GameNode with the opposite color.
traverse_cis
    Traverse descendants of a GameNode with the same color.
yield_lines
    Yield the lines of a file from which Anki can import notes.
"""

import chess.pgn


class ShortStringExporter(chess.pgn.StringExporter):
    """A subclass of StringExporter for one paragraph and no non-FEN headers."""

    def visit_header(self, tagname, tagvalue):
        """Write the header only if tagname == "FEN", with no new lines."""
        if self.headers and tagname == "FEN":
            self.write_token(f'[FEN "{tagvalue}"] ')


def traverse_trans(node):
    """Traverse in post-order descendants of node with the opposite color.

    Follow all node's color's variations and the opposite color's main
    variations.
    """
    for child in node.variations:
        yield from traverse_cis(child)


def traverse_cis(node):
    """Traverse in post-order descendants of node with the same color.

    Follow node's color's main variations and all the opposite color's
    variations.
    """
    yield from traverse_trans(node.variations[0])
    yield node


def yield_lines(node, *, opposite=False):
    """Yield the lines of a file from which Anki can import notes.

    The notes' positions will have the same color, which will differ
    from node's if and only if opposite. The notes will be for node's
    descendants of that color through that color's main variations and
    all the opposite color's variations.
    """
    yield "#separator:tab"
    yield "#html:false"
    yield "#notetype:Chess 2.0"
    for subnode in (traverse_trans if opposite else traverse_cis)(node):
        yield subnode.accept_subgame(ShortStringExporter(columns=None))
