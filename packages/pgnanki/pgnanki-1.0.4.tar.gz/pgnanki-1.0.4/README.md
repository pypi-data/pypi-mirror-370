[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Built with Spacemacs](https://raw.githubusercontent.com/syl20bnr/spacemacs/develop/assets/spacemacs-badge.svg)](https://develop.spacemacs.org)

# Instructions

Install the note type Chess 2.0
[thus](https://github.com/TowelSniffer/Anki-Chess-2.0#getting-started), and
change its card's front and back templates to have `var flip = false;`
[thus](https://youtu.be/NZOK1dZAvpI?t=106). Run `pip install pgnanki`, and in
Python run something like the following.

```Python
import io

import chess.pgn
import pgnanki

pgn = """[FEN "r1bq1bkr/ppp3pp/2n5/3np3/2B5/5Q2/PPPP1PPP/RNB1K2R w KQ - 2 8"]

8. Bxd5+ (8. Qxd5+ Qxd5 (8... Be6 9. Qxe6#) 9. Bxd5+ Be6 10. Bxe6#) 8... Qxd5
(8... Be6 9. Bxe6#) 9. Qxd5+ Be6 10. Qxe6# *"""

with io.StringIO(pgn) as stream:
    game = chess.pgn.read_game(stream)
with open("Fried-Liver-Attack.tsv", "x") as file:
    for line in pgnanki.yield_lines(game, opposite=False):
        print(line, file=file)
```

This example would write to a file named `Fried-Liver-Attack.tsv` the following.

```TSV
#separator:tab
#html:false
#notetype:Chess 2.0
[FEN "r4bkr/ppp3pp/2n1b3/3Qp3/8/8/PPPP1PPP/RNB1K2R w KQ - 1 10"] 10. Qxe6# *
[FEN "r1b2bkr/ppp3pp/2n5/3qp3/8/5Q2/PPPP1PPP/RNB1K2R w KQ - 0 9"] 9. Qxd5+ Be6 10. Qxe6# *
[FEN "r2q1bkr/ppp3pp/2n1b3/3Bp3/8/5Q2/PPPP1PPP/RNB1K2R w KQ - 1 9"] 9. Bxe6# *
[FEN "r1bq1bkr/ppp3pp/2n5/3np3/2B5/5Q2/PPPP1PPP/RNB1K2R w KQ - 2 8"] 8. Bxd5+ ( 8. Qxd5+ Qxd5 ( 8... Be6 9. Qxe6# ) 9. Bxd5+ Be6 10. Bxe6# ) 8... Qxd5 ( 8... Be6 9. Bxe6# ) 9. Qxd5+ Be6 10. Qxe6# *
```

In Anki
1. Click 'File' and 'Import...'.
2. Choose the file like `Fried-Liver-Attack.tsv`.
3. In the dialogue box 'Import File''s section 'Import options' choose the deck.
4. Click Import.

# Documentation

`pgnanki`'s documentation is in its
[docstrings](https://github.com/JohnADawson/pgnanki/blob/master/src/pgnanki.py).

# Copyright and License

Copyright (C) 2025 John Dawson

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, version 3.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
