from pathlib import Path

import Levenshtein as lev
import pandas as pd

from chess_ocr.core import Notation, get_turn_suggestions


def _calculate_cer(recognized_text, ground_truth_text):
    """
    Calculate the Character Error Rate (CER) between the recognized text and the ground truth text.

    Parameters:
    recognized_text (str): The text recognized by the OCR system.
    ground_truth_text (str): The actual correct text (ground truth).

    Returns:
    float: The CER represented as a percentage.
    """
    # Normalize texts: Convert to the same case for fair comparison
    recognized_text = recognized_text.lower()
    ground_truth_text = ground_truth_text.lower()

    # Calculate edit distance
    edit_distance = lev.distance(recognized_text, ground_truth_text)

    # Calculate total characters in ground truth
    total_characters = len(ground_truth_text)

    # Calculate CER
    cer = (edit_distance / total_characters) * 100

    return cer


def _load_my_system_ground_truth():
    my_system_data_path = (
        Path(__file__).parent.parent / "./resources/my_system_ground_truth.csv"
    )
    return pd.read_csv(str(my_system_data_path))


def _evaluate_my_system_notation():
    df_evaulation = _load_my_system_ground_truth()
    # Set the directory path
    dir_path = Path(__file__).parent.parent / "./my_system_notation_samples"
    df_evaulation["OCR"] = df_evaulation.apply(
        lambda x: Notation(str(dir_path / x.Name) + ".png")
        .build_PGN()
        .replace("\n", ""),
        axis=1,
    )
    df_evaulation["OCR_CER"] = df_evaulation.apply(
        lambda x: _calculate_cer(x["OCR"], x["Human Label"]), axis=1
    )

    # turn suggestion should result in notation object
    df_evaulation["OCR_GPT"] = df_evaulation.apply(
        lambda x: get_turn_suggestions(Notation(str(dir_path / x.Name) + ".png"))
        .build_PGN()
        .replace("\n", ""),
        axis=1,
    )
    df_evaulation["OCR_GPT_CER"] = df_evaulation.apply(
        lambda x: _calculate_cer(x["OCR_GPT"], x["Human Label"]), axis=1
    )
    print(df_evaulation.drop(["OCR_GPT", "OCR"], axis=1).to_markdown())
    print(f"Average OCR CER: {df_evaulation['OCR_CER'].mean()}")
    print(f"Average OCR GPT CER: {df_evaulation['OCR_GPT_CER'].mean()}")


if __name__ == "__main__":
    _evaluate_my_system_notation()
