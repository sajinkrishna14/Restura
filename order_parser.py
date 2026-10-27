
import re
import unicodedata


NUMBER_WORDS = {
    # English
    "one": 1, "a": 1, "an": 1,
    "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,

    # Manglish
    "onnu": 1, "oru": 1,
    "randu": 2, "moonnu": 3, "moonu": 3,
    "naalu": 4, "nalu": 4, "naal": 4,
    "anchu": 5, "anju": 5, "aaru": 6,
    "ezhu": 7, "ettu": 8, "ombathu": 9, "pathu": 10,

    # Malayalam
    "ഒന്ന്": 1, "ഒരു": 1,
    "രണ്ട്": 2, "മൂന്ന്": 3, "മൂന്നു": 3,
    "നാല്": 4, "നാലു": 4, "അഞ്ച്": 5,
    "ആറ്": 6, "ഏഴ്": 7, "എട്ട്": 8,
    "ഒമ്പത്": 9, "പത്ത്": 10,
}


def normalise(value):
    value = unicodedata.normalize("NFKC", str(value or "")).casefold()
    value = re.sub(r"[^\w\s]", " ", value)
    return " ".join(value.split())


# Normalise the quantity words once, using the same rules as the transcript.
NORMALISED_NUMBERS = {
    normalise(word): quantity
    for word, quantity in NUMBER_WORDS.items()
}


def _quantity_before_phrase(text, start_position):
    """Extract a number immediately before a matched menu name."""
    prefix = text[:start_position].rstrip()

    # Check digits first, e.g. '2 tea'.
    digit_match = re.search(r"(?<!\w)(\d+)\s*$", prefix)

    if digit_match:
        return max(1, min(int(digit_match.group(1)), 50))

    # Then check words, e.g. 'randu chaya' or 'രണ്ട് ചായ'.
    words = sorted(NORMALISED_NUMBERS, key=len, reverse=True)

    for word in words:
        pattern = r"(?<!\w)" + re.escape(word) + r"\s*$"
        if re.search(pattern, prefix):
            return NORMALISED_NUMBERS[word]

    return 1


def get_item_terms(item):
    terms = [
        normalise(item.get("name")),
        normalise(item.get("malayalam_name")),
    ]

    aliases = item.get("aliases") or []

    if isinstance(aliases, str):
        aliases = [aliases]

    if isinstance(aliases, (list, tuple, set)):
        terms.extend(normalise(alias) for alias in aliases)

    return list(dict.fromkeys(term for term in terms if term))


def match_transcript_to_menu(transcript, menu_items):
    """
    Match database menu names and aliases to the transcript.
    Returns {str(menu_item_id: quantity)}.
    """
    text = normalise(transcript)
    if not text:
        return {}

    candidates = []

    for item in menu_items:
        item_id = str(item.get("id", ""))
        if not item_id:
            continue

        for term in get_item_terms(item):
            candidates.append({
                "item_id": item_id,
                "term": term,
            })

    # Prefer complete names over shorter aliases.
    candidates.sort(key=lambda candidate: len(candidate["term"]), reverse=True)

    matches = {}
    occupied_spans = []

    for candidate in candidates:
        term = candidate["term"]
        pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"

        for found in re.finditer(pattern, text):
            start, end = found.span()

            # Avoid counting the same words twice through overlapping aliases.
            if any(
                start < old_end and end > old_start
                for old_start, old_end in occupied_spans
            ):
                continue

            item_id = candidate["item_id"]
            quantity = _quantity_before_phrase(text, start)

            matches[item_id] = min(
                matches.get(item_id, 0) + quantity,
                50,
            )
            occupied_spans.append((start, end))

    return matches
