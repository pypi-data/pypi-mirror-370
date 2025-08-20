from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from types import MappingProxyType


def make_transliterate_func(
    replacements: Mapping[str, str],
    first_char_replacements: Mapping[str, str],
) -> Callable[[str], str]:
    chars = _build_with_uppercase(replacements)

    def transliterate(text: str, /) -> str:
        if not text:
            return ""

        trie_root = _build_trie(replacements)

        new_text_parts = []
        i = 0
        text_len = len(text)
        while i < text_len:
            node = trie_root
            longest_match_len = 0
            # Find the longest match using the Trie
            for j in range(i, text_len):
                char = text[j].lower()
                if char not in node.children:
                    break

                node = node.children[char]
                if node.value is not None:
                    longest_match_len = j - i + 1

            if longest_match_len > 0:
                original_chunk = text[i : i + longest_match_len]
                key = original_chunk.lower()
                is_first_letter = i == 0 or text[i - 1] not in chars

                current_replacements = replacements
                if is_first_letter and key in first_char_replacements:
                    current_replacements = first_char_replacements

                replacement = current_replacements[key]
                if original_chunk and original_chunk[0].isupper():
                    replacement = replacement.capitalize()

                new_text_parts.append(replacement)
                i += longest_match_len
            else:
                # If no key from replacements matches, handle the character
                char = text[i]
                if char not in chars:
                    new_text_parts.append(char)
                i += 1

        new_text = "".join(new_text_parts)
        if text.isupper():
            return new_text.upper()
        return new_text

    return transliterate


class _TrieNode:
    __slots__ = ("children", "value")

    def __init__(self) -> None:
        self.children: dict[str, _TrieNode] = {}
        self.value: str | None = None


def _build_trie(replacements: Mapping[str, str]) -> _TrieNode:
    root = _TrieNode()
    for key, value in replacements.items():
        node = root
        for char in key:
            node = node.children.setdefault(char, _TrieNode())
        node.value = value
    return root


def _build_with_uppercase(chars: Iterable[str]) -> frozenset[str]:
    chars_set = set(chars)
    for char in chars:
        chars_set.add(char.upper())
    return frozenset(chars_set)


UA_REPLACEMENTS = MappingProxyType(
    {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "h",
        "ґ": "g",
        "д": "d",
        "е": "e",
        "є": "ie",
        "ж": "zh",
        "з": "z",
        "и": "y",
        "і": "i",
        "ї": "i",
        "й": "i",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ь": "",
        "ю": "iu",
        "я": "ia",
        "'": "",
        "зг": "zgh",
    }
)
UA_FIRST_CHAR_REPLACEMENTS = MappingProxyType(
    {
        "є": "ye",
        "ї": "yi",
        "й": "y",
        "ю": "yu",
        "я": "ya",
    }
)


transliterate_ua = make_transliterate_func(
    UA_REPLACEMENTS,
    UA_FIRST_CHAR_REPLACEMENTS,
)
