"""Shared 620px drawing primitives; no network or third-party runtime dependencies."""
import base64
import html
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIDTH = 620
PALETTES = {
    'light': {'ink': '#1f2328', 'muted': '#59636e', 'rule': '#d1d9e0', 'soft': '#f0f2f4'},
    'dark': {'ink': '#e6edf3', 'muted': '#9da7b3', 'rule': '#30363d', 'soft': '#161b22'},
}


def esc(value):
    # Remove characters forbidden in XML 1.0, including API-supplied control bytes.
    return html.escape(re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', str(value)), quote=True)


@lru_cache(maxsize=1)
def font():
    return base64.b64encode((ROOT / 'assets/fonts/plex-mono.woff2').read_bytes()).decode('ascii')


def text(x, y, value, size=12, cls='ink', anchor='start', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(value)}</text>'


def line(x1, y1, x2, y2, cls='rule'):
    return f'<path d="M{x1} {y1}H{x2}" class="{cls}" fill="none" stroke-width="1"/>' if y1 == y2 else f'<path d="M{x1} {y1}L{x2} {y2}" class="{cls}" fill="none"/>'


def rect(x, y, width, height, cls='ink', extra=''):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" class="{cls}" {extra}/>'


def document(title, description, height, body, theme='light', defs=''):
    p = PALETTES[theme]
    style = (f"@font-face{{font-family:ProfileMono;src:url(data:font/woff2;base64,{font()}) format('woff2');font-weight:400}}"
             'text{font-family:ProfileMono,ui-monospace,Menlo,Consolas,monospace;font-variant-ligatures:none}'
             + ''.join(f'.{key}{{fill:{value}}}' for key, value in p.items())
             + f'.rule{{stroke:{p["rule"]};fill:none}}.stroke{{stroke:{p["ink"]};fill:none}}'
             + '@media(prefers-reduced-motion:reduce){.reconstruct{clip-path:none!important}.scan{display:none}}')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="620" height="{height}" viewBox="0 0 620 {height}" role="img" aria-labelledby="title desc">'
            f'<title id="title">{esc(title)}</title><desc id="desc">{esc(description)}</desc>'
            f'<defs><style>{style}</style>{defs}</defs>{body}</svg>\n')


def write_pair(directory, name, title, description, height, body, defs=''):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for theme in PALETTES:
        suffix = '' if theme == 'light' else '-dark'
        content = document(title, description, height, body, theme, defs)
        target = directory / f'{name}{suffix}.svg'
        if not target.exists() or target.read_text() != content:
            target.write_text(content, encoding='utf-8')
