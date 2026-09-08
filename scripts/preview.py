#!/usr/bin/env python3
"""Build an unhosted review harness with light, dark, and narrow compositions."""
import re
from pathlib import Path
from svg import ROOT


def main():
    content = (ROOT/'README.md').read_text()
    content = re.sub(r'<a name="([^"]+)"',r'<a name="user-content-\1"',content)
    content = re.sub(r'<!--[\s\S]*?-->', '', content)
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
    content = content.replace('src="generated/', 'src="../generated/').replace('srcset="generated/', 'srcset="../generated/')
    content = re.sub(r'href="(?!https?://|#)([^"]+)"',r'href="../\1"',content)
    # Use native README HTML plus paragraph wrappers, without a markdown dependency.
    content = '\n'.join('<p>'+block+'</p>' if not block.lstrip().startswith('<') else block for block in content.split('\n\n'))
    def themed(theme):
        result = re.sub(r'<source[^>]+>', '', content)
        if theme == 'dark':
            result = re.sub(r'src="([^"]+)\.svg"',r'src="\1-dark.svg"',result)
        return result
    html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ethan B. Chen / profile proof</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#dce1e6;font:14px/1.7 -apple-system,BlinkMacSystemFont,Arial,sans-serif}header{padding:20px 32px;font:12px monospace;color:#454d56}main{display:flex;align-items:flex-start;gap:24px;padding:0 24px 40px;flex-wrap:wrap}.sheet{width:684px;padding:32px;background:#fff;color:#1f2328;overflow:hidden}.dark{background:#0d1117;color:#e6edf3}.narrow{width:375px;padding:20px}.sheet img{max-width:100%;height:auto;display:block;margin-inline:auto}p{margin:0 0 18px}picture{display:block;margin:0 0 16px}a{color:inherit;text-underline-offset:3px}details{font-size:12px;margin:18px 0}summary{cursor:pointer;color:#76818d}.label{font:10px monospace;letter-spacing:2px;margin:0 0 32px;color:#76818d}
</style><header>ETHAN B. CHEN / README PROOF · LIGHT / DARK / 375PX</header><main>'''
    for label,cls,theme in [('LIGHT','sheet','light'),('DARK','sheet dark','dark'),('MOBILE','sheet narrow','light')]:
        html += f'<article class="{cls}"><div class="label">{label}</div>{themed(theme)}</article>'
    html += '</main></html>'
    (ROOT/'.preview').mkdir(exist_ok=True)
    (ROOT/'.preview/index.html').write_text(html)
    for theme in ('light','dark'):
        page = html[:html.index('<main>')] + f'<main><article class="sheet {theme}">{themed(theme)}</article></main></html>'
        (ROOT/f'.preview/{theme}.html').write_text(page)
    print('Preview: http://localhost:8765/.preview/index.html')


if __name__ == '__main__':
    main()
