import os
from PIL import Image

possible_names = ["my_image.png", "my_image.jpg", "my_image.png.jpg", "my_image.jpeg"]

image_path = None
for name in possible_names:
    if os.path.exists(name):
        image_path = name
        break

if image_path:
    try:
        img = Image.open(image_path)
        img.save("app_icon.ico", format="ICO", sizes=[(256, 256)])
        print(f"🎉 Successfully converted '{image_path}' to 'app_icon.ico'!")
    except Exception as e:
        print(f"Error converting image: {e}")
else:
    print("❌ Image file not found in directory!")