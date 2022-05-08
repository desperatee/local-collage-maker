import datetime
import math
import os
import glob
from io import BytesIO
from random import randint

import requests
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

def getOverlayColor():
    hexColor = os.environ.get('DEFAULT_OVERLAY_COLOR')
    while not hexColor:
        inputHex = input(
            '\nWhat color overlay do you want?\nExample: #B4FBB8\nAnswer \'None\' for no overlay.\n> '
        )
        if inputHex.lower() == 'none':
            return None
        if len(inputHex) in range(6, 7):
            hexColor = inputHex
        else:
            print('Please input a valid hexadecimal color!\n')

    return tuple(int(hexColor.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

def parseImages():
    images = [f for f in glob.glob(f"images/*.{os.environ.get('IMAGE_EXT')}")]


    maxImages = int(os.environ.get('MAX_IMAGES'))
    if len(images) > maxImages:
        images = images[-maxImages:]
        print(f'{len(images)} images found - only {maxImages} are being used!\n')
    else:
        print(f'{len(images)} images found!\n')

    return images


def createCollage(images):
    baseImageSize = (1920, 1080)
    (baseWidth, baseHeight) = baseImageSize
    baseImage = Image.new('RGBA', baseImageSize, 'black')

    dimension = int(os.environ.get('SQUARE_GRID_DIMENSIONS'))
    gridDimensions = (dimension, dimension)  # width, height
    (gridWith, gridHeight) = gridDimensions
    splitWidth, splitHeight = baseWidth / gridWith, baseHeight / gridHeight

    imageScalar = int(os.environ.get('DEFAULT_LAYER_SCALAR'))
    layerSize = (baseWidth // imageScalar, baseHeight // imageScalar)

    imageIndex = len(images) - 1
    numIterations = math.ceil(len(images) / (gridWith * gridHeight))
    for _ in range(numIterations):
        for numCols in range(gridWith):
            for numRows in range(gridHeight):
                posX = \
                    randint(numCols * splitWidth, numCols * (splitWidth + 1)) + 50
                posY = \
                    randint(numRows * splitHeight, numRows * (splitHeight + 1))
                layerPosition = (posX + randint(0, 100), posY)

                image = images[imageIndex]
                try:
                    with open(image, 'rb') as img:
                        discordImg = Image.open(BytesIO(img.read()))
                        discordImg.convert('RGBA')
                        discordImg.thumbnail(layerSize)

                        baseImage.paste(discordImg, layerPosition)
                        print(
                            f'[Img {len(images) - imageIndex}/{len(images)}] Discord image applied as layer...'
                        )
                except Exception as e:
                    print(
                        f'[Img {len(images) - imageIndex}/{len(images)}] Discord image not applied! Error: {e}'
                    )
                    pass

                imageIndex -= 1

                if imageIndex == -1:
                    break

            if imageIndex == -1:
                break
    outDir = 'output.png'
    baseImage.save(outDir)
    print(f'\nImage saved as {outDir}!\n')


if __name__ == "__main__":

    print('\nPulling images from local folder...')
    images = parseImages()
    print(f'Pulled {len(images)} images!')

    print('Creating collage...')
    createCollage(images)
    print('★ Please consider starring the repository here: https://github.com/tfich/auto-collage\n')
