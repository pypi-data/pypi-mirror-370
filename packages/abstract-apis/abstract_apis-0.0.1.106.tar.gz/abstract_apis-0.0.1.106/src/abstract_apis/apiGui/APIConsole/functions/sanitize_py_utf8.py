#!/usr/bin/env python3
# sanitize_py_utf8.py — clean NBSP/BOM/zero-widths + invalid UTF-8 in *.py
import os, sys, io, unicodedata

SKIP = {'.git','venv','.venv','__pycache__','node_modules','build','dist','.mypy_cache','.pytest_cache','.idea','.vscode','.tox','.cache'}

INVISIBLES = {
    '\u00A0': ' ',   # NBSP -> space
    '\ufeff': '',    # BOM char
    '\u200b': '', '\u200c': '', '\u200d': '', '\u2060': '',  # zero-widths
}

def clean_text(s: str) -> str:
    # replace invisibles
    if any(c in s for c in INVISIBLES):
        s = ''.join(INVISIBLES.get(c, c) for c in s)
    # normalize line endings
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    # normalize Unicode form
    s = unicodedata.normalize('NFC', s)
    # drop other control chars (keep \n\t)
    s = ''.join(ch for ch in s if ch >= ' ' or ch in '\n\t')
    return s

def sanitize_bytes(raw: bytes) -> str:
    # strip BOM and common zero-width byte sequences everywhere
    raw = raw.replace(b'\xef\xbb\xbf', b'')  # BOM
    raw = raw.replace(b'\xe2\x80\x8b', b'').replace(b'\xe2\x80\x8c', b'').replace(b'\xe2\x80\x8d', b'').replace(b'\xe2\x81\xa0', b'')
    raw = raw.replace(b'\xc2\xa0', b' ')     # NBSP -> space
    # try utf-8; if it fails, fall back to 'ignore' (we just want the file loadable)
    try:
        s = raw.decode('utf-8')
    except UnicodeDecodeError:
        s = raw.decode('utf-8', errors='ignore')
    return clean_text(s)

def fix_file(path: str) -> bool:
    with open(path, 'rb') as fh:
        raw = fh.read()
    cleaned = sanitize_bytes(raw)
    try:
        prev = raw.decode('utf-8')
    except Exception:
        prev = raw.decode('utf-8', errors='ignore')
    if cleaned != prev or raw != cleaned.encode('utf-8'):
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(cleaned)
        return True
    return False

def main(root: str):
    changed = 0
    for dpath, dnames, fnames in os.walk(root):
        dnames[:] = [d for d in dnames if d not in SKIP]
        for fn in fnames:
            if not fn.endswith('.py'): continue
            p = os.path.join(dpath, fn)
            try:
                if fix_file(p):
                    print(f"fixed: {p}")
                    changed += 1
            except Exception as e:
                print(f"error: {p}: {e}", file=sys.stderr)
    print(f"Done. Files modified: {changed}")

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
