#!/usr/bin/env python3
import sys, os, hashlib, argparse
from pathlib import Path
from datetime import datetime
from pypdf import PdfWriter, PdfReader

# -------------------------------------------------------------------
# quick size formatter - yeah i know there's libraries for this
# -------------------------------------------------------------------
def fmt(b):
    if b < 1_000_000:
        return f"{b/1024:.0f}KB"
    elif b < 1_000_000_000:
        return f"{b/1024/1024:.1f}MB"
    return f"{b/1024/1024/1024:.2f}GB"

def md5(path):
    h = hashlib.md5()
    with open(path,"rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def npages(p):
    try: return len(PdfReader(str(p)).pages)
    except: return 0

# -------------------------------------------------------------------
# actual merge logic
# -------------------------------------------------------------------
def merge(files, dest, pw=None, squeeze=False):
    w = PdfWriter()
    pg = 0
    skipped = []

    for f in files:
        r = PdfReader(str(f))
        if r.is_encrypted:
            skipped.append(f.name)
            continue

        for page in r.pages:
            if squeeze:
                try: page.compress_content_streams()
                except: pass
            w.add_page(page)

        w.add_outline_item(f.stem, pg)
        pg += npages(f)

    if skipped:
        print(f"  skipped (encrypted): {', '.join(skipped)}")

    if pw:
        w.encrypt(user_password=pw, owner_password=pw+"_owner")

    with open(dest, "wb") as out:
        w.write(out)

    return len(skipped)

# -------------------------------------------------------------------
# undo tracking - just stores last output path in home dir
# -------------------------------------------------------------------
TRACKER = Path.home() / ".pdfmp_last"

def save_last(p):
    TRACKER.write_text(str(p))

def do_undo():
    if not TRACKER.exists():
        print("nothing to undo")
        return
    last = Path(TRACKER.read_text().strip())
    TRACKER.unlink()
    if not last.exists():
        print(f"already gone: {last.name}")
        return
    os.remove(last)
    print(f"removed: {last}")

# -------------------------------------------------------------------
# dupe check - compares md5 hashes, not filenames
# -------------------------------------------------------------------
def find_dupes(files):
    seen, dupes = {}, []
    for f in files:
        h = md5(f)
        if h in seen:
            dupes.append((f.name, seen[h].name))
        else:
            seen[h] = f
    return dupes


def main():
    ap = argparse.ArgumentParser(prog="pdfmergepro", add_help=True)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--out", default=None)
    ap.add_argument("--password", default=None)
    ap.add_argument("--compress", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--undo", action="store_true")
    args = ap.parse_args()

    if args.undo:
        do_undo()
        sys.exit(0)

    # collect + validate
    pdfs = [Path(x) for x in args.files if x.lower().endswith(".pdf")]
    bad = [p for p in pdfs if not p.exists()]
    if bad:
        for b in bad: print(f"not found: {b}")
        sys.exit(1)
    if len(pdfs) < 2:
        print("need 2+ pdf files. usage: pdfmergepro a.pdf b.pdf [--out merged.pdf]")
        sys.exit(1)

    # dupe check
    dupes = find_dupes(pdfs)
    if dupes:
        print("\nduplicates found:")
        for a, b in dupes:
            print(f"  {a}  <->  {b}")
        if input("  merge anyway? [y/n]: ").strip().lower() != "y":
            sys.exit(0)

    total_pages = sum(npages(p) for p in pdfs)
    total_size  = sum(p.stat().st_size for p in pdfs)

    dest = Path(args.out) if args.out else Path(f"merged_{datetime.now():%Y%m%d_%H%M%S}.pdf")

    # summary
    print(f"\npdfmergepro")
    print(f"  {len(pdfs)} files  /  {total_pages} pages  /  {fmt(total_size)} input")
    print(f"  -> {dest}")
    if args.compress: print("  compression on")
    if args.password: print("  password protection on")
    if args.dry:      print("  dry run on")
    print()

    for p in pdfs:
        print(f"  {p.name:<45} {npages(p):>4}pp  {fmt(p.stat().st_size):>8}")

    if args.dry:
        print("\n  [dry run] nothing written\n")
        sys.exit(0)

    print("\n  working...", end=" ", flush=True)
    skipped = merge(pdfs, dest, pw=args.password, squeeze=args.compress)
    print("done")

    out_size = dest.stat().st_size
    diff = total_size - out_size
    print(f"\n  output: {fmt(out_size)}", end="")
    if args.compress and diff > 0:
        print(f"  (-{fmt(diff)} saved)", end="")
    print(f"\n  path:   {dest.resolve()}")
    if skipped: print(f"  note:   {skipped} file(s) skipped due to encryption")
    print()

    save_last(dest.resolve())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\ncancelled")
    except ImportError:
        print("run: pip install pypdf")
        sys.exit(1)