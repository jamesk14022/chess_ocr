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
from chess_ocr.core import Notation, build_PGN

extracted_notation = Notation(image_file_path) 
print("Extracted turn text: ", n.turns)
print("Get PGN: ", build_PGN(n.turns))
print("Get Lichess analysis board url: ", n.get_lichess_analysis())
print("Suspicious turns (using pgn-extract): ", n.get_suspicious_turns())
print("Turn suggestions (using openAI GPT API): ", n.get_turn_suggestions())
```

### Performance

Extraction samples from the book "My System" by Aron Nimzowitsch.

|    | Name   | Human Label                                                                                                                                                                       |   OCR_CER |   OCR_GPT_CER |
|---:|:-------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------:|--------------:|
|  0 | ex1    | 1.f5 Kf7 2.Ke5 Ke7 3.f6+ Kf7 4.Kf5 Kf8!                                                                                                                                           |   2.5641  |       2.5641  |
|  1 | ex2    | 8.Ke3 Kc5 9.Kf4!                                                                                                                                                                  |   6.25    |       6.25    |
|  2 | ex3    | 1…Kc6 2.Kg3 Kb7 3.Rf1 Kc6 4.Rf5 Re7 5.h4 Raa7 6.h5 Re6 7.Rf8                                                                                                                      |  15       |      20       |
|  3 | ex4    | 22.Bxe3 Ne8 23.Re2 Ng7 24.Bd2 Nf5! 25.Re1 c5 26.dxc5 Bxc5/                                                                                                                        |   3.44828 |       3.44828 |
|  4 | ex5    | 33…Bc4 34.f4 Ke7 35.Kf2 Kd6 36.Ke3 Kc5                                                                                                                                            |  10.5263  |      10.5263  |
|  5 | ex6    | 27.Ref1 Rhe8 28.e4 Qb5 29.Ra1!                                                                                                                                                    |   3.33333 |       3.33333 |
|  6 | ex7    | 1… Kd6 2.Kf7 Rf1+ 3.Ke8                                                                                                                                                           |  86.9565  |      86.9565  |
|  7 | ex8    | 42.Rd8 Rxa5 43.Rf8+! Kxf8  44.Kxe6                                                                                                                                                |   5.88235 |       5.88235 |
|  8 | ex9    | 50.Kd2 c4 51.Qf1 Qe4 52.Qe2 Ke6 53.Qf1 Ke7! 54.Qe2 b5 55.Qf1 a5 56.Qg1 Qe5 57.Kc2 b4 58.Qf2 Qe4+ 59.Kc1 a4 60.Qg3 b3 61.axb3 cxb3 62.Qc7+ Ke6 63.Qc8+ Kd5 64.Qd7+ Kc4 65.Qf7+ Kd3 |  35.5932  |      36.1582  |
|  9 | ex10   | 1.e4 e5 2. Nf3 d6 3.d4 Bg4? 4.dxe5 Bxf3 5.Qxf3 dxe5 6.Bc4 Nf6 7.Qb3 Qe7 8.Nc3 c6 9.Bg5 b5 10.Nxb5 cxb5 11.Bxb5+ Nbd7                                                              |   4.31034 |       3.44828 |
| 10 | ex11   | 1.Rxf6! Rxf6 2.b4                                                                                                                                                                 |   5.88235 |       5.88235 |
| 11 | ex12   | 1.e4 e5 2.Nf3 Nc6 3.Nc3 Nf6 4.Bb5 Bb4 5.o-o o-o 6.Bxc6 dxc6 7.d3 Bg4 8.h3 Bh5 9.Bg5                                                                                               |  68.6747  |      59.0361  |
| 12 | ex13   | 1.e4 e5 2.Nf3 Nf6 3.Nxe5 d6 4.Nf3 Nxe4 5.d4 Be7 6.Bd3 Nf6 7.o-o Bg4                                                                                                               |   4.41176 |       7.35294 |
| 13 | ex14   | 1.e4 c6 2.d4 d5 3.Nc3 dxe4 4.Nxe4 Nf6 5.Qd3                                                                                                                                       |   2.32558 |       2.32558 |
| 14 | ex15   | 6…Nxd4 7.Qxd4 Ne7 8.Nf3 Nc6 9.Qf4                                                                                                                                                 |   6.06061 |       6.06061 |

Average OCR CER: 17.414631419603275
Average OCR GPT CER: 17.28166642224434
