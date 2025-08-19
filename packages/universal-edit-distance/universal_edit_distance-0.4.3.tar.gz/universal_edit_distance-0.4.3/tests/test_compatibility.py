import datasets
import evaluate
import polars as pl
import pytest
from text_process.normalise import cleanup_spaces
from universal_edit_distance import character_error_rate, word_error_rate


@pytest.fixture
def dataset() -> pl.DataFrame:
    # To see why we are stripping characters and removing multiple spaces
    # see https://gitlab.com/prebens-phd-adventures/universal-edit-distance/-/issues/3
    return (
        datasets.load_dataset("prvInSpace/eval-kaldi-full-model", split="test")
        .select_columns(["sentence", "transcription"])
        .to_polars()
        .with_columns(
            pl.col("sentence")
            .str.strip_chars()
            .map_elements(cleanup_spaces, pl.String),
            pl.col("transcription")
            .str.strip_chars()
            .map_elements(cleanup_spaces, pl.String),
        )
        .filter(pl.col("sentence").str.len_chars() >= 1)
    )


def test_wmer(dataset: pl.DataFrame) -> None:
    wer = evaluate.load("wer")
    jiwer_result = wer.compute(
        predictions=dataset["transcription"], references=dataset["sentence"]
    )
    ued_results = word_error_rate(
        predictions=dataset["transcription"], references=dataset["sentence"]
    )
    assert pytest.approx(jiwer_result) == ued_results


def test_cmer(dataset: pl.DataFrame) -> None:
    cer = evaluate.load("cer")
    jiwer_result = cer.compute(
        predictions=dataset["transcription"], references=dataset["sentence"]
    )
    ued_results = character_error_rate(
        predictions=dataset["transcription"],
        references=dataset["sentence"],
    )
    assert pytest.approx(jiwer_result) == ued_results
