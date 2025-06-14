from PIL import Image

img = Image.open("Wisp_Box.png").convert("RGBA")
bg = Image.new("RGBA", img.size, (0, 0, 0))  # black background
flattened = Image.alpha_composite(bg, img)
flattened.convert("RGB").save("wisp_box_flat.png")
