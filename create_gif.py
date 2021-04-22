import os
from PIL import Image
import sys

def printUsage():
    print("Usage " + sys.argv[0] + " <image> [<image> [...]]")

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        printUsage()
        sys.exit(1)

    outfile = "animation.gif"

    frames = []
    for img in sys.argv[1:]:
        print(img)
        if not os.path.exists(img):
            print("ERROR: file does not exist: " + img)
        else:
            frames.append(Image.open(img))

    frames[0].save(outfile, format="GIF", append_images=frames[1:],
                   save_all=True, duration=500, loop=0)

    print("Finished! GIF created: " + outfile)

# EOF
