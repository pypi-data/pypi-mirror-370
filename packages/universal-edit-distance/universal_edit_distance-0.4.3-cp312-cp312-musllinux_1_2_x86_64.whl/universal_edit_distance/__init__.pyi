from typing import Any, List

# Univeral functions
def universal_error_rate_array(
    predictions: List[List[str]], references: List[List[Any]]
) -> List[float]:
    """Calculates the error-rate for every zipped pair of predictions and references

    WARNING: This function is untested and you should sanity check the output of the function.

    NOTE: Due to limitations of pyo3 they only support a limited number of types. A new generic
    implementation is being tested that should allow a broader set of types as long as __eq__ is
    implemented.
    """

def universal_edit_distance_array(
    predictions: List[List[str]], references: List[List[Any]]
) -> List[int]:
    """Calculates the edit-distance for every zipped pair of predictions and references

    WARNING: This function is untested and you should sanity check the output of the function.

    NOTE: Due to limitations of pyo3 they only support a limited number of types. A new generic
    implementation is being tested that should allow a broader set of types as long as __eq__ is
    implemented.
    """

# Word-based helper functions
def word_error_rate_array(predictions: List[str], references: List[str]) -> List[float]:
    """Calculates the word level error-rate for every zipped pair of predictions and references.
    The delimiter used to split the words is ' '.

    NOTE: If the reference string is empty or contain no words, the resulting WER is inf

    NOTE: Even though the type indicates that the function only takes lists, it takes any iterable
    that can be converted to a Vec<&string> by pyo3.
    """

def word_edit_distance_array(
    predictions: List[str], references: List[str]
) -> List[int]:
    """Calculates the word level edit-distance for every pair in predictions and references.
    The delimiter used to split the words is ' '.

    NOTE: If the reference string is empty or contain no words, the resulting WER is inf

    NOTE: Even though the type indicates that the function only takes lists, it takes any iterable
    that can be converted to a Vec<&string> by pyo3.
    """

def word_error_rate(predictions: List[str], references: List[str]) -> float:
    """Calculates the mean word level error-rate for the entire set.
    This is the equivalent of using the `wer` metric for the `evaluate` library (using `jiwer`).
    The delimiter used to split the words is ' '.

    NOTE: If the reference string is empty or contain no words, the resulting WER is inf

    NOTE: Even though the type indicates that the function only takes lists, it takes any iterable
    that can be converted to a Vec<&string> by pyo3.
    """

# Character-based helper functions
def character_error_rate_array(
    predictions: List[str], references: List[str]
) -> List[float]:
    """Calculates the character level error-rate for every zipped pair of predictions and references.

    NOTE: If the reference string is empty or contain no characters, the resulting CER is inf

    NOTE: Even though the type indicates that the function only takes lists, it takes any iterable
    that can be converted to a Vec<&string> by pyo3.
    """

def character_edit_distance_array(
    predictions: List[str], references: List[str]
) -> List[int]:
    """Calculates the character level edit-distance for every zipped pair of predictions and references.

    NOTE: If the reference string is empty or contain no characters, the resulting CER is inf

    NOTE: Even though the type indicates that the function only takes lists, it takes any iterable
    that can be converted to a Vec<&string> by pyo3.
    """

def character_error_rate(predictions: List[str], references: List[str]) -> float:
    """Calculates the mean word level error-rate for the entire set.
    This is the equivalent of using the `cer` metric for the `evaluate` library (using `jiwer`)

    NOTE: If the reference string is empty or contain no characters, the resulting CER is inf

    NOTE: Even though the type indicates that the function only takes lists, it takes any iterable
    that can be converted to a Vec<&string> by pyo3.
    """

def poi_edit_distance(
    predictions: List[Any], references: List[Any], points_of_interest: List[bool]
) -> List[int]:
    """Calculates the edit distance between the two lists, but only on indicies where points_of_interest is set
    to True. points_of_interest has to be the same length as the reference."""

def poi_error_rate(
    predictions: List[str], references: List[str], points_of_interest: List[bool]
) -> float:
    """Calculates the error distance between the two lists, but only on indicies where points_of_interest is set
    to True. points_of_interest has to be the same length as the reference."""

class Alignment:
    index: int
    start: int
    end: int

def optimal_alignment(predictions: List[Any], references: List[Any]) -> list[Alignment]:
    """Returns a list of alignments for indices in one list to the indicies in the other.
    Note that this is only one of the optimal solutions as there can be multiple optimal alignments"""
