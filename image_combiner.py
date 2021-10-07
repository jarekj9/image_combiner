#!/usr/bin/bash

import os
import argparse
from itertools import cycle
from PIL import Image
from PIL import ImageDraw
from PIL import Image,ImageColor
from PIL import ImageFont
from gooey import Gooey


class ImageCombiner:

    SEPARATOR_WIDTH = 20
    SEPARATOR_COLOR = (0, 0, 0)

    @classmethod
    def combine_horizontal(cls, im1, im2):
        '''Combine images horizontally'''
        combined_im = Image.new('RGB', (im1.width + im2.width + cls.SEPARATOR_WIDTH, max(im1.height, im2.height)))
        separator_im = Image.new("RGB", (cls.SEPARATOR_WIDTH, max(im1.height, im2.height)), cls.SEPARATOR_COLOR)
        combined_im.paste(im1, (0, 0))
        combined_im.paste(separator_im, (im1.width, 0))
        combined_im.paste(im2, (im1.width + cls.SEPARATOR_WIDTH, 0))
        return combined_im

    @classmethod
    def combine_vertical(cls, im1, im2):
        '''Combine images vertically'''
        combined_im = Image.new('RGB', (max(im1.width, im2.width), im1.height + im2.height + cls.SEPARATOR_WIDTH))
        separator_im = Image.new("RGB", (max(im1.width, im2.width), cls.SEPARATOR_WIDTH), cls.SEPARATOR_COLOR)
        combined_im.paste(im1, (0, 0))
        combined_im.paste(separator_im, (0, im1.height))
        combined_im.paste(im2, (0, im1.height + cls.SEPARATOR_WIDTH))
        return combined_im

def give_filenames(name):
	filenames=[]
	all_files=os.listdir('./')
	
	for file in all_files:
		if name.lower() in file.lower():
			filenames.append(file)
	return filenames


@Gooey
def main():
    parser = argparse.ArgumentParser(usage='Choose arguments.')
    parser.add_argument('--vertical', action="store_true", help='Combine images vertically')
    parser.add_argument('--horizontal', action="store_true", help='Combine images horizontally')
    parser.add_argument("--separator_color", choices=["black", "red", "blue"], default="black", help="Choose separator color.")
    parser.add_argument('--separator_width', type=int, default=20, help='Choose separator width.')
    parser.add_argument('--version','-v', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    if args.vertical:
        combine_method = lambda im1, im2: ImageCombiner.combine_vertical(im1, im2)
    elif args.horizontal:
        combine_method = lambda im1, im2: ImageCombiner.combine_horizontal(im1, im2)
    else:
        combine_method = lambda im1, im2: ImageCombiner.combine_vertical(im1, im2)

    if args.separator_color == 'black':
        ImageCombiner.SEPARATOR_COLOR = (0, 0 ,0)
    elif args.separator_color == 'red':
        ImageCombiner.SEPARATOR_COLOR = (255, 0 ,0)
    elif args.separator_color == 'blue':
        ImageCombiner.SEPARATOR_COLOR = (0,0,255)

    ImageCombiner.SEPARATOR_WIDTH = args.separator_width

    files = []
    for format in ['jpg', 'jpeg', 'png', 'bmp', 'gif']:
        files += give_filenames(format)

    if not files:
        exit('There are no supported image files in the folder.')
    im_combined = Image.new("RGB", (1, 1), (255, 255, 255))
    for index, file in enumerate(files):
        im = Image.open(file)
        print(im.format, im.height, im.width)
        if index == 0:
            im_combined = im
            continue
        im_combined = combine_method(im_combined, im)

    im_combined.save("combined.jpg")

if __name__ == '__main__':
    main()

