## ♞ Chess OCR ♞

Extract, parse and find errors in chess notation from PNG images. Algebraic notation without piece graphics is supported, like that found in e.g

- "My System" by Aron Nimzowitsch
- "Silman's Complete Endgame Course" by Jeremy Silman

It does not currently support algebraic notation with piece grapics.

### How to use it

You'll need to a working version of [PGN Extract](https://www.cs.kent.ac.uk/people/staff/djb/pgn-extract/). Compile it and add it to your path. Chess OCR only takes one argument, the input directory of your png samples to be parsed. You can call it with `python3 src/core.py path/to/samples`


