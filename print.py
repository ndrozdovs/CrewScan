from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

fontPath = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
mono_14 = ImageFont.truetype(fontPath, 14)
mono_20 = ImageFont.truetype(fontPath, 20)
 
img = Image.new('RGB', (200, 100), color = (255, 255, 255))

dt_string = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
 
d = ImageDraw.Draw(img)
d.text((25,0), "Visitor Pass", fill=(0,0,0), font=mono_20)
d.text((12,5), "______________", fill=(0,0,0), font=mono_20)
d.text((5,30), "Access to Site Granted:", fill=(0,0,0), font=mono_14)
d.text((20,50), str(dt_string), fill=(0,0,0), font=mono_14)
d.text((150,88), "SetTek", fill=(0,0,0), font=mono_14)
 
img.save('pil_text.png')

#os.system("brother_ql -b pyusb -m QL-700 -p usb://0x04f9:0x2042 print -l 62 pil_text.png")
