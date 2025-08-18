import glob
import os
import tempfile


def expand_wordlist_patterns(wordlist_args: list[str]) -> list[str]:
    """Expand wildcard patterns in wordlist arguments into actual file paths."""
    expanded = []
    for pattern in wordlist_args:
        # glob.glob s absolute path
        matches = [os.path.abspath(p) for p in glob.glob(pattern) if os.path.isfile(p)]
        if matches:
            expanded.extend(matches)
        else:
            if os.path.isfile(pattern):
                expanded.append(os.path.abspath(pattern))
            else:
                raise FileNotFoundError(f"Wordlist not found: {pattern}")
    return expanded

def merge_unique_wordlists(wordlist_paths: list[str]) -> str:
    """Merge multiple wordlist files into a single temporary file with unique entries."""
    unique_words = set()
    for wl_file in wordlist_paths:
        with open(wl_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                print(line)
                if line:
                    unique_words.add(line)
    tmp_fd, tmp_path = tempfile.mkstemp(prefix="ptwebdiscover_wordlist_", suffix=".txt")
    os.close(tmp_fd)
    with open(tmp_path, "w", encoding="utf-8") as out_f:
        for word in sorted(unique_words):
            out_f.write(word + "\n")
    return tmp_path

