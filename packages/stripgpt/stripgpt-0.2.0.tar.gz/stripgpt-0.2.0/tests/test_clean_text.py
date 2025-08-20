import subprocess, sys, os
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / 'src'
if str(SRC_DIR) not in sys.path:
	sys.path.insert(0, str(SRC_DIR))

from stripgpt import clean_text, detect_artifacts, START, END  # type: ignore

SAMPLE = f"Before {START}SECRET{END} After"

def test_span_markers_removed():
	out = clean_text(SAMPLE, kill_bare=False, normalize=True)
	assert START not in out and END not in out
	assert 'SECRET' not in out  # entire span removed
	assert out.startswith('Before') and out.endswith('After')

ZEROWIDTHS = '\u200B\u200C\u200D\u200E\u200F\u202A\u202B\u202C\u202D\u202E'

def test_zero_width_removed():
	txt = f"a{ZEROWIDTHS}b"
	out = clean_text(txt, kill_bare=False, normalize=False)
	assert out == 'ab'

BARE_TOKENS = ["turn2search5", "TuRn12Search15", "L10-L20"]

def test_bare_tokens_removed_when_enabled():
	txt = ' '.join(BARE_TOKENS)
	out = clean_text(txt, kill_bare=True, normalize=True)
	for tok in BARE_TOKENS:
		assert tok.lower() not in out.lower()
	assert out == ''

def test_bare_tokens_preserved_when_disabled():
	txt = ' '.join(BARE_TOKENS)
	out = clean_text(txt, kill_bare=False, normalize=False)
	assert txt == out

def test_whitespace_normalization():
	txt = 'Line 1\t\t  Line 2\n\n  Line 3   '
	out = clean_text(txt, kill_bare=False, normalize=True)
	assert '\t' not in out
	assert '  ' not in out  # double spaces collapsed
	assert out.endswith('Line 3')

def run_cli(args, input_text=None):
	cmd = [sys.executable, '-m', 'stripgpt'] + args
	env = os.environ.copy()
	existing = env.get('PYTHONPATH')
	env['PYTHONPATH'] = str(SRC_DIR) + (':' + existing if existing else '')
	proc = subprocess.run(cmd, input=input_text, text=True, capture_output=True, env=env)
	return proc.returncode, proc.stdout, proc.stderr

def test_cli_stdin_stdout():
	code, out, _ = run_cli([], SAMPLE)
	assert code == 0
	assert 'SECRET' not in out

def test_cli_in_place(tmp_path: Path):
	p = tmp_path / 'sample.txt'
	p.write_text(SAMPLE, encoding='utf-8')
	code, out, _ = run_cli(['-i', str(p)])
	assert code == 0
	assert out == ''
	data = p.read_text(encoding='utf-8')
	assert 'SECRET' not in data

def test_cli_backup(tmp_path: Path):
	p = tmp_path / 'sample.txt'
	p.write_text(SAMPLE, encoding='utf-8')
	code, _, _ = run_cli(['-i', '--backup-suffix', '.orig', str(p)])
	assert code == 0
	backup = p.with_suffix(p.suffix + '.orig')
	assert backup.exists()
	assert backup.read_text(encoding='utf-8') == SAMPLE

def test_cli_kill_bare():
	inp = 'turn2search5 and L12-L14'
	code, out, _ = run_cli(['--kill-bare'], inp)
	assert code == 0
	assert 'turn' not in out.lower()
	assert 'L12' not in out

def test_cli_no_normalize():
	inp = 'A  B\n'
	_, out, _ = run_cli(['--no-normalize'], inp)
	assert out == 'A  B\n'
	_, out2, _ = run_cli([], inp)
	assert out2 == 'A B'

def test_private_use_chars_removed():
	pua_chars = ''.join(chr(cp) for cp in (0xE300, 0xF0000))
	txt = f'A{pua_chars}B'
	out = clean_text(txt, kill_bare=False, normalize=False)
	assert out == 'AB'


def test_detect_artifacts_basic():
	txt = f'X{START}secret{END}Y turn2search5 L10-L11 \u200B'
	rep = detect_artifacts(txt)
	assert rep.get('pua_spans') == 1
	assert rep.get('bare_tokens') == 1
	assert rep.get('line_ranges') == 1
	assert rep.get('zero_width') == 1

def test_cli_detect(tmp_path: Path):
	sample = tmp_path / 'sample.txt'
	sample.write_text(f'A{START}B{END} turn2search5', encoding='utf-8')
	code, out, _ = run_cli(['--detect', str(sample)])
	assert code == 0
	assert 'pua_spans' in out
	assert 'bare_tokens' in out
