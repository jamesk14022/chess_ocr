from openai import OpenAI

piece_suggestion_prefix = """
You are going to be detecting chess moves which are invalid. Assume the use of algebraic chess notation. Attached is some JSON data, containing chess moves. The JSON
contains a list of objects, each object is a turn in a chess game. Each turn contains a move property, this property is an array of objects, each object containing 
some property "move_text", this move text is the output of an OCR system, the move_text property may be incorrect. If you believe it is incorrect, suggest
a correction. Turns which are marked sus: True are more likely to be incorrect. You can add this correction as a property in the same object as the incorrect move_text. Call this property "GPT_correction". Only return 
correct JSON.
"""


def build_combined_move_suggestion_prompt(move_information: str) -> str:
    return piece_suggestion_prefix + "The JSON is as follows: " + move_information


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

    return chat_completion

if __name__ == "__main__":
    print(chat_completion("Say this is a test"))
