"""
Case Change
===========

A package for changing the case of strings.
"""


__version__ = "1.0.1"

def case_change(text: str, mode: str) -> str:
    if mode == "snake":
        return text.replace(" ", "_").lower()
    elif mode == "kebab":
        return text.replace(" ", "-").lower()
    elif mode == "camel":
        words = text.split(" ")
        return words[0].lower() + "".join(word.capitalize() for word in words[1:])
    else:
        raise ValueError("Invalid mode. Choose 'snake', 'kebab', or 'camel'.")
