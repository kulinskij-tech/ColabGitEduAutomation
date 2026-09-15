"""Restore QM1 supplementary notebooks and course links after github-export.

Run with PYTHONPATH=src. Only the exported course is modified.
"""

import argparse
import json
from pathlib import Path
import shutil

from edu_publish.github import apply_colab_export_transformations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--phys4math', type=Path, required=True)
    parser.add_argument('--destination', type=Path, default=Path('published/QuantumMechanics1'))
    args = parser.parse_args()
    target = args.destination / 'QM_py'
    additions = {
        name: args.source / name
        for name in ('qm_technotes.ipynb', 'sinc_wolfram.ipynb', 'rectwv_fresnel.ipynb')
    }
    additions['qm1_qcorr.ipynb'] = args.phys4math / 'phys4math_qm_qcorr.ipynb'
    for source in additions.values():
        json.loads(source.read_text(encoding='utf-8'))
        if source.resolve().is_relative_to(args.destination.resolve()):
            raise ValueError('Supplementary sources must be outside the export')
    for name, source in additions.items():
        shutil.copy2(source, target / name)

    # These former Phys4Math sections are already present in the QM1 course.
    anchors = {
        'qm1_qbitspace.ipynb': {
            'qbit': 'Найпростійшою квантовою системою',
            'ortho': 'Ортопроектор на такий стан:',
        },
        'qm1_ermitop_theor.ipynb': {
            'postpro': 'Перший постулат квантової механіки',
        },
    }
    for name, markers in anchors.items():
        path = target / name
        nb = json.loads(path.read_text(encoding='utf-8'))
        for anchor, marker in markers.items():
            tag = f'<a id="{anchor}"></a>'
            if any(tag in ''.join(c.get('source', [])) for c in nb['cells']):
                continue
            matches = [c for c in nb['cells'] if c['cell_type'] == 'markdown'
                       and marker in ''.join(c.get('source', []))]
            if len(matches) != 1:
                raise ValueError(f'{name}: expected exactly one anchor location for {anchor}')
            cell = matches[0]
            cell['source'] = ''.join(cell['source']).replace(marker, tag + '\n' + marker, 1).splitlines(True)
        path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    base = 'https://colab.research.google.com/github/kulinskij-tech/QuantumMechanics1/blob/main/QM_py/'
    urls = {p.name: base + p.name for p in target.glob('*.ipynb')}
    urls.update({
        'phys4math_qm_axioms1.ipynb': urls['qm1_qbitspace.ipynb'],
        'phys4math_qm_axioms2.ipynb': urls['qm1_ermitop_theor.ipynb'],
        'phys4math_toc.ipynb': urls['qm1_toc.ipynb'],
        'qm2_quasiclass.ipynb': 'https://colab.research.google.com/github/kulinskij-tech/QuantumMechanics2/blob/main/QM_py/qm2_quasiclass.ipynb',
    })
    for path in sorted(target.glob('*.ipynb')):
        apply_colab_export_transformations(path, urls, urls[path.name])
    print(f'Repaired QM1 links and included {len(additions)} supplementary notebooks.')


if __name__ == '__main__':
    main()
