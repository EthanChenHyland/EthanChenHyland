"""Render generated anatomical hop poses as a script-free ASCII sprite sequence."""
import json
from pathlib import Path
from PIL import Image
from svg import ROOT, document, esc


def render_hop(prepare, output, columns=180, gamma=.95):
    config = json.loads((ROOT/'assets/source/frog-hop.json').read_text())
    alt = 'An ASCII frog hopping in a loop: hindlegs crouch, extend at takeoff, and fold back as the front feet reach down to land.'
    # One cell is 600 x 480 source pixels. All poses retain the same scale.
    size = 580 / (columns * .6)
    leading = size * 1.15
    duration = config['duration']
    starts = [0, 22, 34, 45, 60, 74, 100]
    styles = ['.pose{visibility:hidden;animation-duration:%ss;animation-iteration-count:infinite;animation-timing-function:steps(1,end)}' % duration]
    for i in range(6):
        # Visibility changes atomically; no ghosting between distinct limb poses.
        start, end = starts[i:i+2]
        keys = ('0%{visibility:hidden}' if start else '')
        keys += f'{start}%{{visibility:visible}}{end}%{{visibility:hidden}}'
        styles.append(f'.pose-{i}{{animation-name:pose{i}}}@keyframes pose{i}{{{keys}}}')
    styles.append('.pose-0{visibility:visible}@media(prefers-reduced-motion:reduce){.pose{animation:none!important;visibility:hidden!important}.pose-0{visibility:visible!important}}')
    with Image.open(ROOT/'assets/source'/config['sheet']) as sheet:
        for theme in ('light', 'dark'):
            body = ''
            for i, frame in enumerate(config['frames']):
                rows = prepare(sheet, frame['crop'], columns, gamma, frame['matte'], .7, theme)
                dx, dy = frame["offset"]
                body += f'<g class="pose pose-{i}" transform="translate({dx*580/600:.3f} {dy*580/600:.3f})"><text x="20" font-size="{size:.3f}" class="ink" xml:space="preserve">'
                for y, row in enumerate(rows):
                    if row.strip():
                        body += f'<tspan x="20" y="{20+(y+1)*leading:.3f}">{esc(row.rstrip())}</tspan>'
                body += '</text></g>'
            suffix = '-dark' if theme == 'dark' else ''
            Path(output).mkdir(parents=True, exist_ok=True)
            (Path(output)/f'ascii{suffix}.svg').write_text(document('Hopping ASCII frog',alt,490,body,theme,'<style>'+''.join(styles)+'</style>'))
    return alt
