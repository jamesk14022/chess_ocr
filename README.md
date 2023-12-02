## ♞ Chess OCR ♞

Extract, parse and find errors in chess notation from PNG images. Algebraic notation without piece graphics is supported, like that found in e.g

- "My System" by Aron Nimzowitsch
- "Silman's Complete Endgame Course" by Jeremy Silman

It does not currently support algebraic notation with piece grapics.

### How to use it

The program is not available on PyPI, you need to install it from source

```
python setup.py install
```

You'll need to a working version of [PGN Extract](https://www.cs.kent.ac.uk/people/staff/djb/pgn-extract/). Compile it and add it to your path. 

To use GPT to correct notation OCR mistakes, add your OpenAI API key with the environment variable 'OPENAI_API_KEY'. 

```
pip install -r requirements.txt
```

```
from chess_ocr.core import Notation

extracted_notation = Notation(image_file_path) 
print("Extracted turn text: ", n.turns)
print("Get PGN: ", n.build_PGN)
print("Get Lichess analysis board url: ", n.get_lichess_analysis())
print("Suspicious turns (using pgn-extract): ", n.get_suspicious_turns())
print("Turn suggestions (using openAI GPT API): ", n.get_turn_suggestions())
```