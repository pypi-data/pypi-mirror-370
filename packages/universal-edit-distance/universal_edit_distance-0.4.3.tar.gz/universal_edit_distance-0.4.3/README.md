# Universal Edit Distance

**Universal Edit Distance** (or **UED**)(sometimes called **Universal Error Rate** because I struggle to be consistent) is a project aimed at creating a simple Python evaluation library in Rust.

The `universal` part of the name comes from the fact that the Rust implementation is generic and works on any data type that implements `PartialEq` as opposed to most implementations that are limited to only strings.

## ✨ Features
- Much quicker than HuggingFace's `evaluate` library (see benchmarks below)
- Word-error-rate and Character-error-rate functions compatible and comparable with `evaluate`'s `wer` and `cer` metrics.
- Functions that return the `wer` or `cer` for every test as an array within a fraction of second.
- Functions that return the edit distance for every test as an array of integers within the fraction of a second.
- Generic implementations of the `mean-error-rate` and `error-rate` metrics that can work with any* Python type
- Includes type-hints to make development easier.

\* I am pretty sure it works with any type, but it is still being tested

## ⚡️ Quick start
You can now install the library using PyPI! All you need to do is to install the package [universal-edit-distance](https://pypi.org/project/universal-edit-distance/) using your favourite package manager.

**Note:** Pre-compied wheels exists for MacOS and Linux for Python version 3.9 -> 3.13. Builds are not currently working for Windows, so if you are on Windows the package has to be installed from source which requires [cargo](https://doc.rust-lang.org/cargo/getting-started/installation.html) to be installed in your environment.

### Using pip
```bash
pip install universal-edit-distance
```

### Using uv
```bash
uv add universal-edit-distance
```

You should now be able to import the module `universal_edit_distance` in your Python project.

## Example use-case

Since the library is able to work on arbitrary types, you are for example able to do the following.
In the example, we create a class where we override the `__eq__` function to match any word that is in the list of options.
This code outputs `[0, 0, 1]` as expected since "coffi" is not in the list of options.

```python
import universal_edit_distance as ued


class OptionType:
    def __init__(self, options: list[str]):
        self.options = options

    def __eq__(self, value):
        """Checks if the string is in the list of options"""
        if isinstance(value, str):
            return value in self.options
        return False


REFERENCE = ["dw", "i'n", "hoffi", OptionType(["ffotograffi", "photography"])]
HYPO1 = ["dw", "i'n", "hoffi", "ffotograffi"]
HYPO2 = ["dw", "i'n", "hoffi", "photography"]
HYPO3 = ["dw", "i'n", "hoffi", "coffi"]


print(
    ued.universal_edit_distance(
        [HYPO1, HYPO2, HYPO3], [REFERENCE] * 3
    )
)
```

## 🎯 Motivation and why this project exists
I love statistics, and I when I evaluate my speech-recognition models (and other models) I like to run t-tests etc. However, doing that with HuggingFace's `evaluate` library while possible is horrendously slow.

If you only require the mean CER or WER you could continue using `evaluate` and your life would be fine. If you want to be more rigorous in your testing and evaluation, you should consider using this library. 

In addition, one thing that annoys me with a lot of Levenshtein implementations is that the algorithm can literally work on any data type that supports comparison. I have tried to make the implementation found here as generic as possible.

### Benchmarks
**You can find the benchmarking script here: [prebens-phd-adventures/ued-benchmarks](https://gitlab.com/prebens-phd-adventures/ued-benchmarks)**

Note that the single floating point result normally returned from `evaluate` is in this library and in these results called the `mean-error-rate` since it is effectively the mean across all tests as opposed to only a single test. The tests returning a floating point result for each row in the test case is simply called `error-rate`.

The tests in the table below were run using `evaluate=0.4.3`, `jiwer=3.1.0`, and `universal-edit-distance 0.2.0` on a Polars DataFrame containing $n=12775$ entries. For the mean-error-rate results the tests were run 100 times per, and for the error-rate results they were only run once due to `evaluate` being too slow.

| Metric | evaluate | jiwer | ued | Speed-up vs evaluate | Speed-up vs jiwer |
|---|--:|--:|--:|--:|--:|
| Mean WER | 0.31s | 0.16s | 0.02s | 15.28x | 7.75x |
| Mean CER | 0.45s | 0.24s | 0.09s |  5.01x | 2.60x |
| WER | 24.77s | 0.27s | 0.02s | 1137.30x | 12.61x |
| CER | 25.34s | 0.37s | 0.09s | 278.97x | 4.03x | 

As can be seen in the table, `ued` beats `evaluate` and `jiwer` in basically every metric. The goal of the project was to make WER and CER faster, but I'll take the w for the other two.
What you'll also notice is that the results for the mean-error-rates and error-rates are the same for `ued`. That is due to the way it is implemented and is expected.

## 👩‍💻👨‍💻 Contribute to the project
This is my first ever Rust project, so I while I have a vague idea about what I am doing, I am sure it can be improved. If you have any suggestions or requests please feel free to add an issue!

