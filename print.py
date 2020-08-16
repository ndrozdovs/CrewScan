from PIL import Image, ImageDraw, ImageFont
from datetime import date
import os

fontPath = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
font_mono = ImageFont.truetype(fontPath, 14)
 
img = Image.new('RGB', (200, 100), color = (255, 255, 255))

today = date.today()
print("Today's date:", today)
 
d = ImageDraw.Draw(img)
d.text((5,30), "Access to Site Granted:", fill=(0,0,0), font=font_mono)
d.text((60,50), str(today), fill=(0,0,0), font=font_mono)
 
img.save('pil_text.png')

os.system("brother_ql -b pyusb -m QL-700 -p usb://0x04f9:0x2042 print -l 62 pil_text.png")
