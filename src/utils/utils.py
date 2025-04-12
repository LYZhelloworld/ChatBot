import re


def remove_think_tags(text: str) -> str:
    """
    Removes content enclosed within `<think>` and `</think>` tags from the given text.

    - If both opening and closing `<think>` tags are present, the content within the tags is removed.
    - If only the opening `<think>` tag is present without a closing tag, an empty string is returned.
    - If no `<think>` tags are present, the text is returned as-is after trimming whitespace.

    :param str text: The input text to process.
    :return: The processed text with `<think>` tags handled appropriately.
    :rtype: str
    """

    if "<think>" in text and "</think>" in text:
        return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    elif "<think>" in text:
        # The tag is not closed.
        return ""
    else:
        return text.strip()
