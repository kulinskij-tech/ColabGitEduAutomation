"""Apply reviewed Ukrainian prose corrections to QM1 sources, preserving math/code.

Dry-run by default; --apply writes only the reviewed source notebooks.
Backups, a cell-level diff, and validation details are written to --report-dir.
"""

import argparse
import copy
import difflib
import hashlib
import json
from pathlib import Path
import re


# Preserve mathematical notation, code, destinations, and HTML attributes.
PROTECTED = re.compile(
    r'```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`'
    r'|\\begin\{([^}]+)\}[\s\S]*?\\end\{\1\}'
    r'|(?<!\\)\$\$[\s\S]*?(?<!\\)\$\$'
    r'|(?<![\\$])\$(?!\$)[\s\S]*?(?<!\\)\$'
    r'|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)'
    r'|<[^>\n]+>|(?<=\]\()[^)]*(?=\))'
    r'|https?://[^\s<>]+|\\(?:label|ref|eqref|cite|newcommand)\{[^}]*\}'
)
LETTER = 'A-Za-zА-Яа-яІіЇїЄєҐґ'


def rules_from(path):
    rules = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):
            continue
        old, new = line.split('\t')
        if old == new:
            raise ValueError(f'No-op correction: {old}')
        rules.append((re.compile(f'(?<![{LETTER}]){re.escape(old)}(?![{LETTER}])'), new))
    return rules


def correct(text, rules):
    protected = []

    def protect(match):
        protected.append(match.group())
        return f'\x00{len(protected)-1}\x00'

    editable = PROTECTED.sub(protect, text)
    for pattern, replacement in rules:
        editable = pattern.sub(lambda m: replacement, editable)
    result = re.sub(r'\x00(\d+)\x00', lambda m: protected[int(m[1])], editable)
    assert [m.group() for m in PROTECTED.finditer(text)] == [m.group() for m in PROTECTED.finditer(result)]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--localtexmf', type=Path, required=True)
    parser.add_argument('--report-dir', type=Path, required=True)
    parser.add_argument('--rules', type=Path, default=Path('sources/qm1_ua_corrections.tsv'))
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    rules = rules_from(args.rules)
    qm = args.localtexmf / 'Mytex/lectures/quantum/quantumbook/QM_py'
    phys = args.localtexmf / 'Mytex/lectures/Phys4Math/Phys4Math_course'
    paths = sorted(qm.glob('qm1_*.ipynb'))
    paths += [qm / n for n in ('qm_technotes.ipynb', 'sinc_wolfram.ipynb', 'rectwv_fresnel.ipynb')]
    paths += [phys / 'phys4math_qm_qcorr.ipynb']
    args.report_dir.mkdir(parents=True, exist_ok=True)
    report = {'notebooks_checked': len(paths), 'applied': args.apply, 'changed': []}
    diff = []
    pending = []
    for path in paths:
        raw = path.read_bytes()
        original = json.loads(raw)
        edited = copy.deepcopy(original)
        changed_cells = []
        for i, cell in enumerate(edited['cells']):
            if cell['cell_type'] != 'markdown':
                continue
            old = ''.join(cell.get('source', []))
            new = correct(old, rules)
            if new != old:
                cell['source'] = new.splitlines(True) if isinstance(cell['source'], list) else new
                changed_cells.append(i)
                diff.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                            fromfile=f'{path.name}:cell-{i}:before', tofile=f'{path.name}:cell-{i}:after'))
        # Verify every property except Markdown source is untouched.
        stripped = copy.deepcopy(edited)
        for i in changed_cells:
            stripped['cells'][i]['source'] = original['cells'][i]['source']
        assert stripped == original, path
        if not changed_cells:
            continue
        relative = path.relative_to(args.localtexmf)
        backup = args.report_dir / 'source-before' / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists() and backup.read_bytes() != raw:
            raise ValueError(f'Existing backup differs; choose a new report directory: {backup}')
        backup.write_bytes(raw)
        after = (json.dumps(edited, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
        preview = args.report_dir / 'source-after' / relative
        preview.parent.mkdir(parents=True, exist_ok=True)
        preview.write_bytes(after)
        pending.append((path, raw, after))
        report['changed'].append({'source': relative.as_posix(), 'cells': changed_cells,
                                 'before_sha256': hashlib.sha256(raw).hexdigest(),
                                 'after_sha256': hashlib.sha256(after).hexdigest()})
    (args.report_dir / 'prose.diff').write_text(''.join(diff), encoding='utf-8')
    if args.apply:
        # Check all inputs before writing, so concurrent edits are not overwritten.
        for path, before, _ in pending:
            if path.read_bytes() != before:
                raise ValueError(f'Source changed during review: {path}')
        for path, _, after in pending:
            path.write_bytes(after)
    report['changed_notebooks'] = len(pending)
    report['changed_markdown_cells'] = sum(len(e['cells']) for e in report['changed'])
    (args.report_dir / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'changed'}))


if __name__ == '__main__':
    main()
