Word Error Rate (WER)
=====================

The `WER` module contains functions related to word error rates and the helper functions word error distance.
These functions are wrappers around their :ref:`universal_error_rate` counter-parts, but where the vectors of strings are converted into lists of words first.
This is done on whitespace.

The `word_error_rate` function is compatible and comparable with the equivalent functions in `evaluate <https://github.com/huggingface/evaluate>`_ and `jiwer <https://github.com/jitsi/jiwer>`_. 



.. code-block:: python
    :linenos:

    from universal_edit_distance import word_error_rate, word_error_rate_array
    word_error_rate(["hello world"], ["helo world"]) # returns 0.5
    word_error_rate_array(["hello world"], ["helo world"]) # returns [0.5]

Functions
---------

.. autofunction:: universal_edit_distance.word_edit_distance_array

.. autofunction:: universal_edit_distance.word_error_rate

.. autofunction:: universal_edit_distance.word_error_rate_array