#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from .core import clean_text, detect_artifacts
from . import __version__

def process_path(p: Path, *, inplace: bool, backup_suffix: str, enc: str,
				 kill_bare: bool, normalize: bool) -> None:
	data = p.read_text(encoding=enc, errors='replace')
	cleaned = clean_text(data, kill_bare=kill_bare, normalize=normalize)
	if inplace:
		if backup_suffix:
			p.with_suffix(p.suffix + backup_suffix).write_text(data, encoding=enc)
		p.write_text(cleaned, encoding=enc)
	else:
		sys.stdout.write(cleaned)

def main(argv=None):
	ap = argparse.ArgumentParser(
		description="stripgpt: Remove ChatGPT markers (PUA, hidden chars, optional leftover tokens)."
	)
	ap.add_argument('paths', nargs='*', help='Files to clean. Reads stdin if none given.')
	ap.add_argument('-i', '--in-place', action='store_true', help='Write back to file instead of stdout.')
	ap.add_argument('--backup-suffix', default='', help='Backup original with this suffix before overwrite.')
	ap.add_argument('--encoding', default='utf-8', help='Text encoding (default: utf-8).')
	ap.add_argument('--kill-bare', action='store_true',
					help='Also remove bare tokens like turn2search5 and L10-L20.')
	ap.add_argument('--no-normalize', action='store_true',
					help='Keep whitespace as-is (no trimming/compacting).')
	ap.add_argument('--detect', action='store_true',
					help='Only detect and report artifact counts (JSON) per file/stdin; do not modify output.')
	ap.add_argument('-V', '--version', action='store_true', help='Print version and exit.')
	args = ap.parse_args(argv)

	try:
		if args.version:
			sys.stdout.write(f"stripgpt {__version__}\n")
			return 0
		if args.paths:
			for s in args.paths:
				p = Path(s)
				data = p.read_text(encoding=args.encoding, errors='replace')
				if args.detect:
					import json
					rep = detect_artifacts(data)
					rep['file'] = str(p)
					sys.stdout.write(json.dumps(rep, ensure_ascii=False) + '\n')
				else:
					process_path(p, inplace=args.in_place, backup_suffix=args.backup_suffix,
								 enc=args.encoding, kill_bare=args.kill_bare,
								 normalize=not args.no_normalize)
		else:
			data = sys.stdin.read()
			if args.detect:
				import json
				rep = detect_artifacts(data)
				sys.stdout.write(json.dumps(rep, ensure_ascii=False) + '\n')
			else:
				cleaned = clean_text(data, kill_bare=args.kill_bare, normalize=not args.no_normalize)
				sys.stdout.write(cleaned)
		return 0
	except Exception as e:  # pragma: no cover
		sys.stderr.write(f"stripgpt error: {e}\n")
		return 1

if __name__ == '__main__':  # pragma: no cover
	sys.exit(main())

