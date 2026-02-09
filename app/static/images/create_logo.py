from PIL import Image, ImageDraw, ImageFont
import os

# Создаем изображение 300x100
img = Image.new('RGB', (300, 100), color=(255, 255, 255))
draw = ImageDraw.Draw(img)

# Фон
draw.rectangle([0, 0, 300, 100], fill=(233, 245, 233))  # Светло-зеленый фон

# Круг с буквой R
draw.ellipse([20, 20, 80, 80], fill=(76, 175, 80), outline=(56, 142, 60), width=3)

# Буква R внутри круга
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
except:
    font = ImageFont.load_default()

# Рисуем букву R
draw.text((40, 40), "R", fill=(255, 255, 255), font=font, anchor="mm")

# Текст "ResFormPRO"
try:
    font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
except:
    font_text = ImageFont.load_default()

draw.text((100, 40), "ResFormPRO", fill=(46, 125, 50), font=font_text, anchor="lm")

# Подзаголовок
try:
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
except:
    font_sub = ImageFont.load_default()

draw.text((100, 65), "Школа 'Ресурс'", fill(46, 125, 50), font=font_sub, anchor="lm")

# Сохраняем
img.save('logo.png')
print('✓ Логотип создан: logo.png')
