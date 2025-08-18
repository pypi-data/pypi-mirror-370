"""
Small program that takes a markdown file as input.
The headlines are extracted and put and parsed into a table of contents with chapter numbers
"""

import argparse
import re

# todo: run tests automatically


def open_file(path: str) -> list:
    """
    open and read file. Return content as list split on line breaks
    :return: list
    """
    with open(
        path,
        "r",
    ) as f:
        file = f.read()
        file = file.splitlines()
    return file


def extract_all_headlines(file: list) -> list:
    """
    filter lines in file and return only those that are marked as a headline
    :param file: list of strings
    :return: smaller list of strings, all starting with "#"
    """
    headlines = [line for line in file if line.startswith("#")]
    return headlines


def detect_max_depth(headlines: list) -> int:
    """
    detect the maximum depth the chapter numbers of the TOC will need
    :param headlines: list of strings starting with "#"
    :return: int
    """
    depth = max([hl.count("#") for hl in headlines])
    return depth


def reset_counter(counter, old_pos):
    for i, c in enumerate(counter):
        if i >= old_pos:
            counter[i] = 0

    return counter


def remove_trailing_zeros(counter: list) -> list:
    """remove trailing zeros from counter recursively"""
    if counter[-1] == 0:
        counter = remove_trailing_zeros(counter[:-1])
    return counter


def link_headline(hl: str) -> str:
    """make actual headline into a link"""

    hl = hl.strip("#").strip().lower()
    hl = re.sub(r" ", "-", hl)
    hl = re.sub(r"\.", "", hl)
    hl = f"#{hl}"
    return hl


def add_depth(headlines: list, max_depth: int) -> list:
    """
    add chapter numbers of correct depth to each headline. remove the markdown marker. add indentation based on depth
    :param headlines: list of strings starting with "#"
    :param max_depth: integer of the depth the ToC should take
    :return: list of new strings
    """
    result = []
    counter = [0] * max_depth
    old_pos = 0
    for hl in headlines:
        pos = hl.count("#") - 1
        if pos < old_pos:
            counter = reset_counter(counter, old_pos)
        counter[pos] = counter[pos] + 1
        removed_zeros = remove_trailing_zeros(counter)
        new_headline = ".".join(str(el) for el in removed_zeros) + " [" + hl.strip("#").strip() + "]"
        linked_headline = link_headline(hl)
        new_headline = f"{'\t'*pos}- {new_headline}({linked_headline})"
        result.append(new_headline)
        old_pos = pos
    return result


def assemble_toc(headlines: list) -> str:
    """parse headline list to string"""
    toc = "# Table of Contents\n"
    toc += "\n".join(headlines)
    return toc


def write_toc(path, toc):
    with open(path, "r+") as file:
        content = file.read()
        file.seek(0, 0)
        file.write(toc.rstrip("\r\n") + "\n" + content)


def parse_args():
    """Parse cmd-line arguments"""
    parser = argparse.ArgumentParser(
        prog="Methodical",
        description="Extract headlines from a markdown file to write a ToC to the top of the file",
    )

    parser.add_argument("filename")

    args = parser.parse_args()

    return args


def main():
    args = parse_args()
    file = open_file(args.filename)
    headlines = extract_all_headlines(file)
    max_depth = detect_max_depth(headlines)
    headlines = add_depth(headlines, max_depth)
    toc = assemble_toc(headlines)
    write_toc(args.filename, toc)
    print(toc)
    return headlines


if __name__ == "__main__":
    main()
