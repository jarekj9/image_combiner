#!/usr/bin/env python

import os
import math
import argparse
from typing import List, Callable
from PIL import Image, ImageColor
from gooey import Gooey
from gooey import GooeyParser


class ImageCombiner:

    def __init__(self, separator_color, separator_width):
        self.separator_color = separator_color
        self.separator_width = separator_width

    def combine_horizontal(self, im1: Image, im2: Image) -> Image:
        '''Combine images horizontally'''
        combined_im = Image.new('RGB', (im1.width + im2.width + self.separator_width, max(im1.height, im2.height)))
        separator_im = Image.new("RGB", (self.separator_width, max(im1.height, im2.height)), self.separator_color)
        combined_im.paste(im1, (0, 0))
        combined_im.paste(separator_im, (im1.width, 0))
        combined_im.paste(im2, (im1.width + self.separator_width, 0))
        return combined_im

    def combine_vertical(self, im1: Image, im2: Image) -> Image:
        '''Combine images vertically'''
        combined_im = Image.new('RGB', (max(im1.width, im2.width), im1.height + im2.height + self.separator_width))
        separator_im = Image.new("RGB", (max(im1.width, im2.width), self.separator_width), self.separator_color)
        combined_im.paste(im1, (0, 0))
        combined_im.paste(separator_im, (0, im1.height))
        combined_im.paste(im2, (0, im1.height + self.separator_width))
        return combined_im

    def custom_combine(self, files: List[str], row_images_count=1) -> Image:
        '''Combine images in rectangular form'''
        im_combined = Image.new("RGB", (1, 1), (255, 255, 255))
        row_combined = Image.new("RGB", (1, 1), (255, 255, 255))
        image_rows = math.ceil(len(files) / row_images_count)

        print(f'Files: {len(files)}, image rows: {image_rows}, images in row: {row_images_count}')
        for row_index in range(image_rows):
            next_range_start = row_index * row_images_count
            next_range_stop = row_index * row_images_count + row_images_count

            print(f'Processing row: {row_index + 1} of {row_images_count}')
            row_combined = self.combine_in_line(files[next_range_start: next_range_stop])

            if row_index == 0:
                im_combined = row_combined
                continue

            im_combined = self.combine_vertical(im_combined, row_combined)
        return im_combined

    def combine_in_line(self, files: List[str], combine_method: Callable = None) -> Image:
        '''Combine images in one row'''
        if not combine_method:
            combine_method = self.combine_horizontal
        im_combined = Image.new("RGB", (1, 1), (255, 255, 255))
        for image_index in range(len(files)):
            print(f'Processing image: {image_index + 1} of {len(files)} in row, Name: {files[image_index]}', end=', ')
            im = Image.open(files[image_index])
            print(f'Spec: {im.format}, {im.height}x{im.width}')
            if image_index == 0:
                im_combined = im
                continue
            im_combined = combine_method(im_combined, im)
        return im_combined


def give_filenames(name: str):
    filenames = []
    all_files = os.listdir('./')

    for file in all_files:
        if name.lower() in file.lower():
            filenames.append(file)
    return filenames


@Gooey(show_restart_button=False)
def main():
    parser = GooeyParser(description="Program will combine all images in current folder into combined.jpg.")
    parser.add_argument("--method", choices=["vertical", "horizontal", "custom"], default="vertical", help="Choose combine method: vertical, horizontal or custom(rectangular).")
    parser.add_argument('--custom_row_length', type=int, default=1, help='Only for custom method. Choose how many images are combined in each row.')
    parser.add_argument('--separator_color', default="#000000", help="Choose separator color.", widget='ColourChooser') 
    parser.add_argument('--separator_width', type=int, default=20, help='Choose separator width.', widget='Slider')
    parser.add_argument('--version', '-v', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    files = []
    for format in ['jpg', 'jpeg', 'png', 'bmp', 'gif']:
        files += give_filenames(format)
    if not files:
        exit('There are no supported image files in the folder.')

    separator_color = ImageColor.getcolor(args.separator_color, "RGB")

    print('Starting')
    combiner = ImageCombiner(separator_color, args.separator_width)

    if args.method == "custom":
        im_combined = combiner.custom_combine(files, args.custom_row_length)
    elif args.method == "vertical":
        im_combined = combiner.combine_in_line(files, combine_method=combiner.combine_vertical)
        im_combined.save("combined.jpg")
    elif args.method == "horizontal":
        im_combined = combiner.combine_in_line(files, combine_method=combiner.combine_horizontal)
        im_combined.save("combined.jpg")
    else:
        im_combined = combiner.combine_in_line(files, combine_method=combiner.combine_vertical)

    print('Saving image')
    im_combined.save("combined.jpg")
    print('Done.\n')


if __name__ == '__main__':
    main()
