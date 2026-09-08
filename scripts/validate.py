#!/usr/bin/env python3
"""Validate XML, asset references, and byte-for-byte offline reproducibility."""
import ast
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from svg import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for script in ROOT.glob('scripts/*.py'):
        ast.parse(script.read_text(), filename=str(script))
    files = sorted((ROOT/'generated').glob('*.svg'))
    assert files, 'No SVG files generated'
    for path in files:
        root = ET.parse(path).getroot()
        assert root.attrib['viewBox'].startswith('0 0 620 '), path
        assert root.find('{http://www.w3.org/2000/svg}title') is not None, path
        assert root.find('{http://www.w3.org/2000/svg}desc') is not None, path
        assert path.stat().st_size < 150_000, f'Oversized graphic: {path}'
        for node in root.iter():
            assert node.tag.rsplit('}',1)[-1] not in {'script','foreignObject'}, path
            assert not any(k.lower().startswith('on') for k in node.attrib), path
    readme = (ROOT/'README.md').read_text()
    for name in re.findall(r'(?:src|srcset)="([^"]+)"',readme):
        assert (ROOT/name).is_file(), f'Missing image {name}'
    anchors = set(re.findall(r'<a (?:name|id)="([^"]+)"',readme))
    links = re.findall(r'\]\(([^)]+)\)',readme) + re.findall(r'href="([^"]+)"',readme)
    for name in links:
        if name.startswith('#'):
            assert name[1:].removeprefix('user-content-') in anchors, f'Missing section anchor {name}'
        if not name.startswith(('https://','http://','#')):
            assert (ROOT/name).exists(), f'Missing link {name}'
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        readme_copy = directory/'README.md'
        shutil.copy2(ROOT/'README.md',readme_copy)
        subprocess.run([sys.executable,str(ROOT/'scripts/generate_profile.py'),'--snapshot',str(ROOT/'generated/activity.json'),
            '--output',str(directory/'generated'),'--readme',str(readme_copy)],check=True)
        if (ROOT/'assets/source/hero.png').exists():
            subprocess.run([sys.executable,str(ROOT/'scripts/make_ascii.py'),str(ROOT/'assets/source/hero.png'),
                '--output',str(directory/'generated'),'--readme',str(readme_copy)],check=True)
        for path in (directory/'generated').iterdir():
            assert digest(path) == digest(ROOT/'generated'/path.name), f'Non-deterministic: {path.name}'
        assert digest(readme_copy) == digest(ROOT/'README.md'), 'Non-deterministic README'
    print(f'PASS: {len(files)} SVGs, Python syntax, README paths, and deterministic regeneration.')


if __name__ == '__main__':
    main()
