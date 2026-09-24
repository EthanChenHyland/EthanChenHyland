#!/usr/bin/env python3
"""Reconstruct the user's source image as an animated ASCII SVG, using Pillow.

Example: python scripts/make_ascii.py assets/source/hero.png
An explicit --crop left,top,right,bottom overrides conservative border trimming.
The original input is never modified. The configured profile uses generated hop poses.
"""
import argparse
import json
from pathlib import Path
import re

from PIL import Image
from ascii_art import prepare
from svg import ROOT, esc, text, write_pair, document
from generate_profile import picture





def render_ascii(rows,out,alt,theme=None):
    fontsize = min(7.8, 580/(len(rows[0])*0.6))
    leading = fontsize*1.15
    left = (620-len(rows[0])*fontsize*0.6)/2
    height = round(30+len(rows)*leading)
    body = '<g transform="translate(31 85) scale(.9)"><g class="frog-idle"><g class="reconstruct" clip-path="url(#reveal)">'
    for i,row in enumerate(rows):
        body += text(round(left,3),round(15+(i+1)*leading,3),row.rstrip(),round(fontsize,3),extra='xml:space="preserve"')
    body += '</g></g></g>'
    # The underlying clip is fully open: unsupported SMIL still shows the image.
    defs = (f'<clipPath id="reveal"><rect width="620" height="{height}">'
            f'<animate attributeName="height" from="0" to="{height}" dur="1.6s" begin="0s" repeatCount="1" fill="freeze"/>'
            '</rect></clipPath>')
    # Transform only the artwork; the SVG viewport and surrounding README stay fixed.
    defs += (f'<style>.frog-idle{{transform-origin:310px {height-15}px;'
             'animation:frogIdle 2.8s ease-in-out 0s infinite}'
             '@keyframes frogIdle{'
             '0%,100%{transform:translate(0,0) rotate(0deg) scale(1,1)}'
             '10%{transform:translate(0,0) rotate(-3deg) scale(1.07,.84)}'
             '25%{transform:translate(18px,-60px) rotate(5deg) scale(.94,1.08)}'
             '38%{transform:translate(24px,0) rotate(2deg) scale(1.09,.82)}'
             '46%{transform:translate(16px,-12px) rotate(-4deg) scale(.98,1.02)}'
             '54%{transform:translate(0,0) rotate(3deg) scale(1.04,.94)}'
             '63%{transform:translate(-10px,0) rotate(-4deg) scale(1.07,.86)}'
             '77%{transform:translate(-24px,-48px) rotate(-6deg) scale(.94,1.07)}'
             '90%{transform:translate(-12px,0) rotate(-2deg) scale(1.09,.84)}}'
             '@media(prefers-reduced-motion:reduce){'
             '.frog-idle{animation:none!important;transform:none!important}}'
             '</style>')
    height += 100  # Headroom for jumps and rotation, without clipping or layout shifts.
    if theme is None:
        write_pair(out,'ascii','ASCII reconstruction',alt,height,body,defs)
    else:
        Path(out).mkdir(parents=True,exist_ok=True)
        suffix = '-dark' if theme == 'dark' else ''
        (Path(out)/f'ascii{suffix}.svg').write_text(document('ASCII reconstruction',alt,height,body,theme,defs))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--crop',type=lambda s: tuple(map(int,s.split(','))))
    parser.add_argument('--config',type=Path,default=ROOT/'assets/source/hero.json')
    parser.add_argument('--columns',type=int)
    parser.add_argument('--gamma',type=float)
    parser.add_argument('--alt')
    parser.add_argument('--output',type=Path,default=ROOT/'generated')
    parser.add_argument('--readme',type=Path,default=ROOT/'README.md')
    args = parser.parse_args()
    config = json.loads(args.config.read_text()) if args.config.exists() else {}
    args.columns = args.columns or config.get('columns',124)
    args.gamma = args.gamma if args.gamma is not None else config.get('gamma',0.85)
    args.crop = args.crop or config.get('crop')
    args.alt = args.alt or config.get('alt','The supplied hero image reconstructed in monochrome ASCII characters.')
    if not 40 <= args.columns <= 180 or not 0.2 <= args.gamma <= 3:
        parser.error('Use 40–180 columns and gamma 0.2–3')
    if args.crop and len(args.crop) != 4:
        parser.error('Crop needs four comma-separated coordinates')
    if (ROOT/'assets/source/frog-hop.json').exists() and args.source.resolve() == (ROOT/'assets/source/hero.png').resolve():
        from frog_frames import render_hop
        args.alt = render_hop(prepare,args.output,args.columns,args.gamma)
    else:
        with Image.open(args.source) as source:
            for theme in ('light','dark'):
                rows = prepare(source,args.crop,args.columns,args.gamma,config.get('matte'),config.get('matte_feather',1.1),theme)
                render_ascii(rows,args.output,args.alt,theme)
    content,count = re.subn(r'(<!-- hero:start -->).*?(<!-- hero:end -->)',
        lambda m: m[1]+'\n'+picture('ascii',args.alt).replace('width="620"','width="540"')+'\n\n'+m[2],args.readme.read_text(),flags=re.S)
    if count != 1:
        raise ValueError('README must contain one hero marker pair')
    args.readme.write_text(content)
    print(f'ASCII reconstruction: {args.columns} columns')


if __name__ == '__main__':
    main()
