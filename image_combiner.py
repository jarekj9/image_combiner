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

    def __init__(self, separator_color, separator_width):
        self.separator_color = separator_color
        self.separator_width = separator_width

    def combine_horizontal(self, im1, im2):
        '''Combine images horizontally'''
        combined_im = Image.new('RGB', (im1.width + im2.width + self.separator_width, max(im1.height, im2.height)))
        separator_im = Image.new("RGB", (self.separator_width, max(im1.height, im2.height)), self.separator_color)
        combined_im.paste(im1, (0, 0))
        combined_im.paste(separator_im, (im1.width, 0))
        combined_im.paste(im2, (im1.width + self.separator_width, 0))
        return combined_im

    def combine_vertical(self, im1, im2):
        '''Combine images vertically'''
        combined_im = Image.new('RGB', (max(im1.width, im2.width), im1.height + im2.height + self.separator_width))
        separator_im = Image.new("RGB", (max(im1.width, im2.width), self.separator_width), self.separator_color)
        combined_im.paste(im1, (0, 0))
        combined_im.paste(separator_im, (0, im1.height))
        combined_im.paste(im2, (0, im1.height + self.separator_width))
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
    parser.add_argument("--method", choices=["vertical", "horizontal"], default="vertical", help="Choose combine method: vertical or horizontal.")
    parser.add_argument("--separator_color", choices=["black", "red", "blue"], default="black", help="Choose separator color.")
    parser.add_argument('--separator_width', type=int, default=20, help='Choose separator width.')
    parser.add_argument('--version','-v', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    if args.separator_color == 'black':
        separator_color = (0, 0, 0)
    elif args.separator_color == 'red':
        separator_color = (255, 0, 0)
    elif args.separator_color == 'blue':
        separator_color = (0, 0, 255)

    combiner = ImageCombiner(separator_color, args.separator_width)

    if args.method == "vertical":
        combine_method = lambda im1, im2: combiner.combine_vertical(im1, im2)
    elif args.method == "horizontal":
        combine_method = lambda im1, im2: combiner.combine_horizontal(im1, im2)
    else:
        combine_method = lambda im1, im2: combiner.combine_vertical(im1, im2)

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

