#!/usr/bin/env python3
"""Reconstruct the user's source image as a one-shot ASCII SVG, using Pillow.

Example: python scripts/make_ascii.py assets/source/hero.png
An explicit --crop left,top,right,bottom overrides conservative border trimming.
The original input is never modified. No substitute image is created.
"""
import argparse
import json
from pathlib import Path
import re

from PIL import Image, ImageChops, ImageFilter, ImageOps, ImageDraw
from svg import ROOT, esc, text, write_pair, document
from generate_profile import picture

RAMP = ' .,:;irsXA253hMHGS#9B&@'


def prepare(source, crop=None, columns=124, gamma=0.85, matte=None, matte_feather=1.1, theme='light'):
    image = ImageOps.exif_transpose(source).convert('RGBA')
    if matte:
        mask = Image.new('L', image.size, 0)
        ImageDraw.Draw(mask).polygon([tuple(p) for p in matte], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(matte_feather))
        image.putalpha(ImageChops.multiply(image.getchannel('A'), mask))
    alpha_box = image.getchannel('A').getbbox()
    if not alpha_box:
        raise ValueError('The source image is fully transparent')
    if crop:
        left, top, right, bottom = crop
        if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
            raise ValueError('Crop must be inside the source image')
        image = image.crop(crop)
    elif alpha_box != (0,0,image.width,image.height):
        image = image.crop(alpha_box)
    background = Image.new('RGBA',image.size,'white')
    background.alpha_composite(image)
    gray = ImageOps.grayscale(background)
    alpha = image.getchannel('A')
    # Trim only near-uniform light borders, never assume a face or crop the center.
    if not crop:
        corners = [gray.getpixel(p) for p in ((0,0),(gray.width-1,0),(0,gray.height-1),(gray.width-1,gray.height-1))]
        if min(corners) > 235 and max(corners)-min(corners) < 12:
            diff = ImageChops.difference(gray,Image.new('L',gray.size,round(sum(corners)/4)))
            box = diff.point(lambda p: 255 if p > 22 else 0).getbbox()
            if box:
                pad = max(4,round(min(gray.size)*0.035))
                trim = (max(0,box[0]-pad),max(0,box[1]-pad),min(gray.width,box[2]+pad),min(gray.height,box[3]+pad))
                gray = gray.crop(trim)
                alpha = alpha.crop(trim)
    # 0.60-em glyph width / 1.15-em line height maintains the source aspect ratio.
    rows = max(1,round(gray.height/gray.width*columns*0.60/1.15))
    if rows > 88:
        columns = max(12,round(columns*88/rows))
        rows = 88
    gray = ImageOps.autocontrast(gray,cutoff=0.5)
    gray = gray.resize((columns,rows),Image.Resampling.LANCZOS)
    gray = gray.filter(ImageFilter.MedianFilter(3))
    gray = gray.filter(ImageFilter.UnsharpMask(radius=1,percent=140,threshold=4))
    table = [round(255*(i/255)**gamma) for i in range(256)]
    gray = gray.point(table)
    alpha = alpha.resize((columns,rows),Image.Resampling.LANCZOS)
    def glyph(x,y):
        value = gray.getpixel((x,y))/255
        opacity = alpha.getpixel((x,y))/255
        density = (1-value) if theme == 'light' else max(0,value-(1-opacity))
        return RAMP[round(density*(len(RAMP)-1))]
    return [''.join(glyph(x,y) for x in range(columns)) for y in range(rows)]


def render_ascii(rows,out,alt,theme=None):
    fontsize = min(7.8, 580/(len(rows[0])*0.6))
    leading = fontsize*1.15
    left = (620-len(rows[0])*fontsize*0.6)/2
    height = round(30+len(rows)*leading)
    body = '<g class="reconstruct" clip-path="url(#reveal)">'
    for i,row in enumerate(rows):
        body += text(round(left,3),round(15+(i+1)*leading,3),row.rstrip(),round(fontsize,3),extra='xml:space="preserve"')
    body += '</g>'
    # The underlying clip is fully open: unsupported SMIL still shows the image.
    defs = (f'<clipPath id="reveal"><rect width="620" height="{height}">'
            f'<animate attributeName="height" from="0" to="{height}" dur="1.6s" begin="0s" repeatCount="1" fill="freeze"/>'
            '</rect></clipPath>')
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
    with Image.open(args.source) as source:
        for theme in ('light','dark'):
            rows = prepare(source,args.crop,args.columns,args.gamma,config.get('matte'),config.get('matte_feather',1.1),theme)
            render_ascii(rows,args.output,args.alt,theme)
    content,count = re.subn(r'(<!-- hero:start -->).*?(<!-- hero:end -->)',
        lambda m: m[1]+'\n<a href="assets/source/hero.png" title="View the original photograph">\n'+picture('ascii',args.alt).replace('width="620"','width="540"')+'\n</a>\n\n'+m[2],args.readme.read_text(),flags=re.S)
    if count != 1:
        raise ValueError('README must contain one hero marker pair')
    args.readme.write_text(content)
    print(f'ASCII reconstruction: {len(rows[0])} columns × {len(rows)} rows')


if __name__ == '__main__':
    main()
