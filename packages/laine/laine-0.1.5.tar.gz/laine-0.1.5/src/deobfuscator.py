from PIL import Image

def detect_transparent_strip(img):
    width, height = img.size
    max_transparent_width = 0
    for x in reversed(range(width)):
        if all(img.getpixel((x, y))[3] == 0 for y in range(height)):
            max_transparent_width += 1
        else:
            break
    return max_transparent_width


def deobfuscate(img, width, height):
    spacing_w, spacing_h = (width // 32) * 8, (height // 32) * 8
    dst = Image.new("RGBA", (width, height))

    for x in range(0, width - spacing_w + 1, spacing_w):
        for y_offset in range(0, height - spacing_h + 1, spacing_h):
            initial_y_start = (x // spacing_w) * spacing_h + spacing_h
            for y in range(initial_y_start, height - spacing_h + 1, spacing_h):
                old_rect = (x, y, x + spacing_w, y + spacing_h)
                new_x = (y // spacing_h) * spacing_w
                new_y = (x // spacing_w) * spacing_h
                new_rect = (new_x, new_y, new_x + spacing_w, new_y + spacing_h)
                dst.paste(img.crop(new_rect), old_rect[:2])
                dst.paste(img.crop(old_rect), new_rect[:2])

    for i in range(4):
        mx, my = i * spacing_w, i * spacing_h
        if mx + spacing_w <= width and my + spacing_h <= height:
            mid_rect = (mx, my, mx + spacing_w, my + spacing_h)
            dst.paste(img.crop(mid_rect), mid_rect[:2])

    if width % spacing_w:
        box = (width - (width % spacing_w), 0, width, height)
        dst.paste(img.crop(box), (width - (width % spacing_w), 0))

    if height % spacing_h:
        box = (0, height - (height % spacing_h), width, height)
        dst.paste(img.crop(box), (0, height - (height % spacing_h)))

    return dst


def restore_right_strip(deob_img, orig_img, width, height, strip_width):
    if strip_width > 0:
        box = (width - strip_width, 0, width, height)
        strip = orig_img.crop(box)
        deob_img.paste(strip, (width - strip_width, 0))