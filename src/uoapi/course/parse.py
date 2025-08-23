"""
HTML parsing utilities for University of Ottawa course data.

This module provides functions to extract course information from
HTML pages scraped from the University of Ottawa course catalog.
"""

from typing import cast, Tuple, List, Union
from bs4 import Tag, NavigableString

from uoapi.course import utils, patterns as pt
from uoapi.course.models import Subject, Prerequisite, Component


def title_tag(tag: Union[Tag, NavigableString]) -> Tuple[str, str, int]:
    """
    Extract course code, title, and credits from a course block title tag.

    Args:
        tag: BeautifulSoup tag containing course title information

    Returns:
        Tuple of (course_code, title, credits)

    Example:
        >>> tag = Tag(name='div')
        >>> tag.string = "CSI3140 World Wide Web Programming (3 credits)"
        >>> title_tag(tag)
        ('CSI3140', 'World Wide Web Programming', 3)
    """
    title = utils.replace_special_spaces(tag.text)

    code = utils.extract_codes(title, False)[0]
    title = utils.remove_codes(title)

    credits = utils.extract_credits(title)
    title = utils.remove_credits(title)

    if (course_match := pt.code_groups.search(code)) is None:
        raise ValueError(f"Could not parse course code {code}")

    code = cast(str, course_match.groups()[1]).upper()

    return code, title, credits


def description_tag(tag: Tag | NavigableString | None) -> str:
    """
    Extracts the description of a course from a courseblockdesc tag
    """
    if tag is None:
        return ""

    description = utils.replace_special_spaces(tag.text)
    return description


def subject_tag(tag: Tag, url_prefix: str):
    if not tag.has_attr("href"):
        # TODO: Add log message here or crash
        return None

    match tag.string, tag["href"]:
        case str(label), str(href):
            path = utils.get_last_path_component(href)
            subject = utils.clean_subject_label(label)
            subject_code = path.upper()

            return Subject(
                subject=subject,
                subject_code=subject_code,
                link=url_prefix + path + "/",  # type: ignore  # pyright: ignore
            )
        case s, h:
            raise ValueError(f"Expected strings, got {type(s)} and {type(h)}")


def extras_blocks(tags: list[Tag]) -> tuple[str, str]:
    """
    Extracts the prerequisites and components
    from a list of courseblockextra tags

    Args:
        tags: The list of courseblockextra tags

    Returns:
        A tuple containing the prerequisites and component strings.
        If the prerequisites or components are not found, an empty string
        is returned for that value.
    """
    blocks: list[Prerequisite | Component] = []

    for tag in tags:
        block = (
            utils.replace_special_spaces(tag.text).strip(".").strip().strip(".").strip()
        )

        if component := Component.try_parse(block):
            blocks.append(component)
        if prerequisite := Prerequisite.try_parse(block):
            blocks.append(prerequisite)

    match blocks:
        case [Prerequisite(content=block)]:
            return block, ""
        case [Component(content=block)]:
            return "", block
        case [Prerequisite(content=prereq), Component(content=comp)]:
            return prereq, comp
        case [Component(content=comp), Prerequisite(content=prereq)]:
            return prereq, comp
        case _:
            return "", ""

    return "", ""
