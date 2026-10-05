"""Independent pre-code prefix-max oracle; no production imports."""

from itertools import product


def prefix_comparisons(seed, tokens):
    """Return numeric before/after and relation from whole prefixes."""
    return [(max([seed, *tokens[:i]]), (value > max([seed, *tokens[:i]]))
             - (value < max([seed, *tokens[:i]])), max([seed, *tokens[:i + 1]]))
            for i, value in enumerate(tokens)]


def finite_traces():
    for seed in range(4):
        for length in range(6):
            for tokens in product((1, 2, 3), repeat=length):
                yield seed, list(tokens), prefix_comparisons(seed, list(tokens))
