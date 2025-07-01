from PIL import Image, ImageDraw

# Create a 32x32 image with a transparent background
img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# Draw a simple circle
draw.ellipse([4, 4, 28, 28], fill='blue')

# Save as ICO
img.save('favicon.ico')
