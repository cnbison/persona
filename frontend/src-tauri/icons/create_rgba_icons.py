from PIL import Image, ImageDraw

# 创建32x32 RGBA图标
img = Image.new('RGBA', (32, 32), color=(59, 130, 246, 255))  # 蓝色背景
draw = ImageDraw.Draw(img)
draw.text((8, 8), "AI", fill=(255, 255, 255, 255))  # 白色文字
img.save('32x32.png')
print("✅ Created 32x32.png (RGBA)")

# 创建128x128 RGBA图标
img = Image.new('RGBA', (128, 128), color=(59, 130, 246, 255))
draw = ImageDraw.Draw(img)
draw.text((48, 48), "AI", fill=(255, 255, 255, 255))
img.save('128x128.png')
print("✅ Created 128x128.png (RGBA)")

# 创建256x256 RGBA图标 (@2x)
img = Image.new('RGBA', (256, 256), color=(59, 130, 246, 255))
draw = ImageDraw.Draw(img)
draw.text((112, 112), "AI", fill=(255, 255, 255, 255))
img.save('128x128@2x.png')
print("✅ Created 128x128@2x.png (RGBA)")

# 创建macOS .icns图标（可选）
# icns需要特殊工具，暂时跳过

print("\n✅ 所有RGBA图标创建完成！")
