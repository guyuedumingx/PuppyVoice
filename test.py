from PIL import Image
filename = "./resources/puppy.png"
img = Image.open(filename)
img.save('puppy.ico')