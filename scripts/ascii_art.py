"""Shared photograph-to-ASCII conversion for the hero and pond sprites."""
from PIL import Image, ImageChops, ImageFilter, ImageOps, ImageDraw

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

