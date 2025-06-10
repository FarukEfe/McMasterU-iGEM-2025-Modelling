from fuzzywuzzy import fuzz

def sort_by_similarity(strings: list[tuple[str,str]], ref: str):
    return sorted(strings, key=lambda s: max(fuzz.ratio(ref, s[0]), fuzz.ratio(ref, s[1])), reverse=True)