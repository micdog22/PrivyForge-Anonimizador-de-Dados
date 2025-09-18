import hashlib, random

def _sha(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def apply_hash(val: str, salt: str, length: int = 16) -> str:
    return _sha(salt + str(val))[:max(4, min(length, 64))]

def apply_mask(val: str, show_first: int = 0, show_last: int = 0, char: str = "*") -> str:
    s = str(val)
    if not s: return s
    n = len(s)
    keep_first = max(0, min(show_first, n))
    keep_last = max(0, min(show_last, n - keep_first))
    middle = max(0, n - keep_first - keep_last)
    return s[:keep_first] + (char * middle) + s[n-keep_last:]

def apply_random_number(val: str, salt: str, min_v: int, max_v: int) -> int:
    h = _sha(salt + str(val))
    seed = int(h[:16], 16)
    r = random.Random(seed)
    return r.randint(min_v, max_v)
