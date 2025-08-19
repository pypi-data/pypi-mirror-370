Character Error Rate (CER)
==========================

The `CER` functions are functions related to character error rates and the helper functions character error distance.
These functions are wrappers around their :ref:`universal_error_rate` counter-parts, but where the vectors of strings are converted into lists of characters first.

The `character_error_rate` function is compatible and comparable with the equivalent function in `jiwer <https://github.com/jitsi/jiwer>`_. 
It is only almost compatible with `evaluate <https://github.com/huggingface/evaluate>`_ since evaluate removes duplicate spaces before giving them to `jiwer`.
Since the functions here and in `jiwer` does not modify the strings, they might return different results than `evaluate` if you do not normalise the whitespace in the input strings.

Functions
---------

.. autofunction:: universal_edit_distance.character_edit_distance_array

.. autofunction:: universal_edit_distance.character_error_rate

.. autofunction:: universal_edit_distance.character_error_rate_array