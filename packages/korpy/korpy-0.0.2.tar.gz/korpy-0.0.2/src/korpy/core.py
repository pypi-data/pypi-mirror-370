from typing import Literal, Union
vowels = ["ㅏ","ㅐ","ㅑ","ㅒ","ㅓ","ㅔ","ㅕ","ㅖ","ㅗ","ㅘ","ㅙ","ㅚ","ㅛ","ㅜ","ㅝ","ㅞ","ㅟ","ㅠ","ㅡ","ㅢ","ㅣ"]
consonants = ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]
finals = ["","ㄱ","ㄲ","ㄳ","ㄴ","ㄵ","ㄶ","ㄷ","ㄹ","ㄺ","ㄻ","ㄼ","ㄽ","ㄾ","ㄿ","ㅀ","ㅁ","ㅂ","ㅄ","ㅅ","ㅆ","ㅇ","ㅈ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]
def is_korean(char: str) -> bool:
    cp = ord(char)
    return (
        0x1100 <= cp < 0x1200 or 
        0x3130 <= cp < 0x3190 or 
        0xA960 <= cp < 0xA980 or 
        0xD7B0 <= cp < 0xD800 or 
        0xAC00 <= cp <= 0xD7A3
    )
def group(group_name: Literal['Hangul Jamo', 'Hangul Compatibility Jamo', 'Hangul Jamo Extended-A', 'Hangul Jamo Extended-B', 'Hangul Syllables']) -> range:
    match group_name:
        case 'Hangul Jamo':
            return range(0x1100, 0x1200)
        case 'Hangul Compatibility Jamo':
            return range(0x3130, 0x3190)
        case 'Hangul Jamo Extended-A':
            return range(0xA960, 0xA980)
        case 'Hangul Jamo Extended-B':
            return range(0xD7B0, 0xD800)
        case 'Hangul Syllables':
            return range(0xAC00, 0xD7A3)
def _esc(s: str):
    return "".join(
        "\\u{:04X}".format(ord(c)) if ord(c) <= 0xFFFF else "\\U{:08X}".format(ord(c))
        for c in s
    )
def _no_finals():
    return [0xAC00 + (L * 21 * 28) + (V * 28) for L in range(19) for V in range(21)]
def _with_finals():
    return [0xAC00 + (L * 21 * 28) + (V * 28) + T for L in range(19) for V in range(21) for T in range(1, 28)]
def _find(obj, sized):
    try:
        return sized.index(obj)
    except ValueError:
        return None
def combine(s: Union[str, bytes], *, ensure_korean: bool = True, only_syl: bool = False) -> Union[str, bytes]:
    savetype = type(s)
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    generated_string = []
    nofinals = _no_finals()
    for char in s:
        if generated_string and generated_string[-1] in consonants and char in vowels:
            idx_c = _find(generated_string[-1], consonants) or 0
            idx_v = _find(char, vowels) or 0
            new_unicode = 0xAC00 + idx_c * 21 * 28 + idx_v * 28
            generated_string[-1] = chr(new_unicode)
            continue
        if generated_string and ord(generated_string[-1]) in nofinals and char in finals:
            old_unicode = ord(generated_string[-1])
            idx_t = _find(char, finals) or 0
            new_unicode = old_unicode + idx_t
            generated_string[-1] = chr(new_unicode)
            continue
        if ensure_korean and not is_korean(char):
            generated_string.append(_esc(char))
        else:
            generated_string.append(char)
    if only_syl and len(generated_string) > 1:
        raise ValueError("found multi-syllable string")
    result = "".join(generated_string)
    if savetype is bytes:
        result = result.encode("utf-8")
    return result
def extend(s: Union[str, bytes], *, ensure_korean: bool = True, only_syl: bool = False) -> Union[str, bytes]:
    savetype = type(s)
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    if only_syl and len(s) > 1:
        raise ValueError("found multi-syllable string")
    generated_string = []
    for char in s:
        if not is_korean(char):
            if ensure_korean:
                generated_string.append(_esc(char))
            else:
                generated_string.append(char)
            continue
        old_unicode = ord(char) - 0xAC00
        idx_c = old_unicode // (21 * 28)
        idx_v = (old_unicode % (21 * 28)) // 28
        idx_t = (old_unicode % (21 * 28)) % 28
        generated_string.append(consonants[idx_c])
        generated_string.append(vowels[idx_v])
        generated_string.append(finals[idx_t])
    result = "".join(generated_string)
    if savetype is bytes:
        result = result.encode("utf-8")
    return result

def get_sound(s: Union[str, bytes], *, only_korean: bool = True) -> Union[str, bytes]:
    generated_string = ""
    consonants_match = {"ㄱ": "g", "ㄲ": "kk", "ㄴ": "n", "ㄷ": "d", "ㄸ": "tt", "ㄹ": "r", "ㅁ": "m", "ㅂ": "b", "ㅃ": "pp", "ㅅ": "s", "ㅆ": "ss", "ㅇ": "",  "ㅈ": "j", "ㅉ": "jj", "ㅊ": "ch", "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "h"}
    vowels_match = {"ㅏ": "a","ㅐ": "ae","ㅑ": "ya","ㅒ": "yae","ㅓ": "eo","ㅔ": "e","ㅕ": "yeo","ㅖ": "ye","ㅗ": "o","ㅘ": "wa","ㅙ": "wae","ㅚ": "oe","ㅛ": "yo","ㅜ": "u","ㅝ": "wo","ㅞ": "we","ㅟ": "wi","ㅠ": "yu","ㅡ": "eu","ㅢ": "ui","ㅣ": "i"}
    finals_match = {"": "", "ㄱ": "k","ㄲ": "k","ㄳ": "k","ㄴ": "n","ㄵ": "n","ㄶ": "n","ㄷ": "t","ㄹ": "l","ㄺ": "k","ㄻ": "m","ㄼ": "p","ㄽ": "l","ㄾ": "l","ㄿ": "p","ㅀ": "l","ㅁ": "m","ㅂ": "p","ㅄ": "p","ㅅ": "t","ㅆ": "t","ㅇ": "ng","ㅈ": "t","ㅊ": "t","ㅋ": "k","ㅌ": "t","ㅍ": "p","ㅎ": "t"}
    for char in s:
        if only_korean and not is_korean(char):
            raise ValueError(f"Non-Korean character detected: {char}")
        initial, vowel, final = extend(char)
        generated_string += consonants_match.get(initial, "")
        generated_string += vowels_match.get(vowel, "")
        generated_string += finals_match.get(final, "")
    return generated_string