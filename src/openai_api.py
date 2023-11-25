from openai import OpenAI
import json

SAMPLE_PGN = "1. e4 e5 2. Nf3 Nc6 3. Nc3 Nf6 4. Bb5 Bb4 5. 0-0 0-0 6. Bxc6 dxc6 7. 03 Bg4"

piece_suggestion_prefix = """
You are going to be detecting chess moves which are invalid. Assume the use of algebraic chess notation. Attached is some JSON data, containing chess moves. The JSON
contains a list of objects, each object is a turn in a chess game. Each turn contains a move property, this property is an array of objects, each object containing 
some property "move_text", this move text is the output of an OCR system, the move_text property may be incorrect. If you believe it is incorrect, suggest
a correction. Turns which are marked sus: True are more likely to be incorrect. You can add this correction as a property in the same object as the incorrect move_text. Call this property "GPT_correction". Only return 
correct JSON.
"""

next_move_prediction_prompt = """
You are going to be detecting if the final chess move of white in a sequence is invalid. I will provide you with a piece of chess PGN notation. The final move
in the sequence by white may be invalid. If you believe the white move is invalid, please suggest a valid move. Please respond with a JSON object with two keys:
'is_valid_white' and 'move_suggestion_white'. Set is_valid_white to true if the final move is correct, else false. If the move appears to be invalid, 
please use the move_suggestion_white key to suggest a valid move. Only respond with JSON, no additional content. Do not include the move number in the move_suggestion_white.
"""

next_move_validation_prompt = """
You are going to be detecting if the final chess move of white has valid algebraic notation. We are not interested in whether the move is a valid chess move, only if the move 
text follows the rules of algebraic notation. I will provide you with a piece of chess PGN notation. The final move
in the sequence by white may be invalid. If you believe the white move is invalid, please suggest a valid move. This text is extracted with OCR, the OCR engine may have made a mistake.
Please respond with a JSON object with two keys: 'is_valid_white' and 'move_suggestion_white'. Set is_valid_white to true if the final move is correct, else false. If the move appears to be invalid, 
please use the move_suggestion_white key to suggest a valid move, considering the valid move may be similar because of the OCR mistake. Only respond with JSON, no additional content. Do not include the move number in the move_suggestion_white.
"""

algebraic_validation_prompt = """
You are going to be detecting if the final chess move of white has valid algebraic notation. We are not interested in whether the move is a valid chess move, only if the move 
text follows the rules of algebraic notation. I will provide you with a piece of chess PGN notation. The final move
in the sequence by white may be invalid. If you believe the white move is invalid, please suggest a valid move. This text is extracted with OCR, the OCR engine may have made a mistake.
Please respond with a JSON object with two keys: 'is_valid_white' and 'move_suggestion_white'. Set is_valid_white to true if the final move is correct, else false. If the move appears to be invalid, 
please use the move_suggestion_white key to suggest a valid move, considering the valid move may be similar because of the OCR mistake. Only respond with JSON, no additional content. Do not include the move number in the move_suggestion_white.
"""

algebraic_movetext_validation_prompt = """
You are going to be detecting if a piece of algebraic chess notation is valid. We are not interested in whether the move is a valid chess move, only if the move 
text follows the rules of algebraic notation. If you believe the move text is invalid, please suggest a valid move. This text is extracted with OCR, the OCR engine may have made a mistake.
Please respond with a JSON object with two keys: 'is_valid' and 'move_text_suggestion'. Set is_valid to true if the move text appears to be valid, else false. If the move appears to be invalid, 
please use the move_text_suggestion key to suggest a valid move, considering the valid move may be similar because of the OCR mistake. Only respond with JSON, no additional content. 
"""

def build_combined_move_suggestion_prompt(move_information: str) -> str:
    return piece_suggestion_prefix + "The JSON is as follows: " + move_information

def build_next_move_prediction_prompt(PGN: str) -> str:
    return next_move_validation_prompt + "The PGN is as follows: " + PGN

def build_algebraic_movetext_prompt(move_text: str) -> str:
    return algebraic_movetext_validation_prompt + "The move text is as follows: " + move_text

def test_next_move_prediction(PGN: str) -> dict:
    prompt = build_next_move_prediction_prompt(PGN)
    return json.loads(chat_completion(prompt))

def test_valid_algebraic(move_text: str) -> dict:
    prompt = build_algebraic_movetext_prompt(move_text)
    return json.loads(chat_completion(prompt))

def chat_completion(prompt: str):
    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4",
    )
    #print(chat_completion)
    return chat_completion.choices[0].message.content

if __name__ == "__main__":
    #print(chat_completion("Say this is a test"))
    test_next_move_prediction(SAMPLE_PGN)
