import pytest
from methodical.main import (
    extract_all_headlines,
    open_file,
    detect_max_depth,
    add_depth,
    reset_counter,
    assemble_toc,
    remove_trailing_zeros,
    link_headline,
)

data = """# Headline 1

blabla

## Headline 1.1

## Headline 1.2

### Headline 1.2.1

## Headline 1.3
"""

data_cleaned = [
    "# Headline 1",
    "",
    "blabla",
    "",
    "## Headline 1.1",
    "",
    "## Headline 1.2",
    "",
    "### Headline 1.2.1",
    "",
    "## Headline 1.3",
]
headlines = ["# Headline 1", "## Headline 1.1", "## Headline 1.2", "### Headline 1.2.1", "## Headline 1.3"]


def test_open():
    path = "tests/test_example.md"
    actual = open_file(path)
    data_ = data.splitlines()
    assert actual == data_


def test_extract():
    len_headlines = 5
    actual = len(extract_all_headlines(data_cleaned))

    assert actual == len_headlines


def test_detect_max():
    actual = detect_max_depth(data_cleaned)
    assert actual == 3


@pytest.mark.parametrize(
    "headline, expected",
    (
        ["# Headline 1", "#headline-1"],
        ["## Headline 1.1", "#headline-11"],
        ["## Headline 1.2", "#headline-12"],
        ["### Headline 1.2.1", "#headline-121"],
        ["## Headline 1.3", "#headline-13"],
    ),
)
def test_link_headline(headline, expected):
    actual = link_headline(headline)

    assert actual == expected


def test_add_depth():
    actual = add_depth(headlines, 3)
    expected = [
        "- 1 [Headline 1](#headline-1)",
        "\t- 1.1 [Headline 1.1](#headline-11)",
        "\t- 1.2 [Headline 1.2](#headline-12)",
        "\t\t- 1.2.1 [Headline 1.2.1](#headline-121)",
        "\t- 1.3 [Headline 1.3](#headline-13)",
    ]
    assert actual == expected


def test_resset_counter():
    counter = [1, 2, 3]
    new_counter = [1, 2, 0]

    actual = reset_counter(counter, old_pos=2)

    assert actual == new_counter


def test_assemble_toc():
    expected = """# Table of Contents
- 1 [Headline 1](#headline-1)
\t- 1.1 [Headline 1.1](#headline-11)
\t- 1.2 [Headline 1.2](#headline-12)
\t\t- 1.2.1 [Headline 1.2.1](#headline-121)
\t- 1.3 [Headline 1.3](#headline-13)"""

    input_ = [
        "- 1 [Headline 1](#headline-1)",
        "\t- 1.1 [Headline 1.1](#headline-11)",
        "\t- 1.2 [Headline 1.2](#headline-12)",
        "\t\t- 1.2.1 [Headline 1.2.1](#headline-121)",
        "\t- 1.3 [Headline 1.3](#headline-13)",
    ]
    actual = assemble_toc(input_)
    assert actual == expected


def test_remove_trailing_zeros():
    counter = [1, 0, 0]
    actual = remove_trailing_zeros(counter)
    expected = [1]

    assert actual == expected
