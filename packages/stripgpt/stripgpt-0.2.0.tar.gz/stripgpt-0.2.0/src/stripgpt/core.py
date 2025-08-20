"""Core cleaning logic for stripgpt."""
from __future__ import annotations
import re
import unicodedata

START = '\ue200'
END = '\ue201'

PUA_SPAN = re.compile(rf'{START}[\s\S]*?{END}')
ZW_DIR   = re.compile(r'[\u200B\u200C\u200D\u200E\u200F\u202A-\u202E\u2060\u2066-\u2069]')
BARE_TOKEN = re.compile(r'\bturn\d+\w*\d+\b', re.IGNORECASE)
LINE_RANGE = re.compile(r'\bL\d+-L\d+\b')

def clean_text(txt: str, *, kill_bare: bool, normalize: bool) -> str:
	t = PUA_SPAN.sub('', txt)
	t = ''.join(ch for ch in t if unicodedata.category(ch) != 'Co')
	t = ZW_DIR.sub('', t)
	if kill_bare:
		t = BARE_TOKEN.sub('', t)
		t = LINE_RANGE.sub('', t)
	if normalize:
		t = re.sub(r'[ \t]+', ' ', t)
		t = re.sub(r'[ \t]+\n', '\n', t)
		t = t.strip()
	return t

def detect_artifacts(txt: str) -> dict:
	"""Detect ChatGPT / LLM export artifacts without modifying text.

	Returns a dict with counts for each artifact category. A category absent (count 0)
	indicates that artifact type was not detected.
	Categories:
	  - pua_spans: number of start/end marker spans (START..END) found
	  - pua_chars: count of standalone private-use characters (category 'Co') remaining after removing spans virtually
	  - zero_width: count of zero-width / bidi control characters
	  - bare_tokens: count of tokens like turn2search5
	  - line_ranges: count of line range tokens like L10-L20
	"""
	report: dict[str, int] = {}
	# Count spans
	spans = list(PUA_SPAN.finditer(txt))
	if spans:
		report['pua_spans'] = len(spans)
	# Remove spans virtually to avoid double counting their interior PUA chars
	tmp = PUA_SPAN.sub('', txt)
	# Count private-use characters
	pua_chars = [ch for ch in tmp if unicodedata.category(ch) == 'Co']
	if pua_chars:
		report['pua_chars'] = len(pua_chars)
	# Zero-width / bidi control
	zw = ZW_DIR.findall(tmp)
	if zw:
		report['zero_width'] = len(zw)
	# Bare tokens
	bt = BARE_TOKEN.findall(tmp)
	if bt:
		report['bare_tokens'] = len(bt)
	lr = LINE_RANGE.findall(tmp)
	if lr:
		report['line_ranges'] = len(lr)
	return report

__all__ = ['clean_text', 'detect_artifacts', 'START', 'END']

