#!/usr/bin/env python

import os
import sys
import math
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

        print(f'Files: {len(files)}, image rows: {image_rows}, images in row: {row_images_count}', flush=True)
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
            print(f'Processing image: {image_index + 1} of {len(files)} in row, Name: {files[image_index]}', end=', ', flush=True)
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

def calculte_row_length(image_count: int, aspect_ratio: float) -> int:
    '''Calculate how many images should be in a row,
    aspect_ratio is images number to images number, not pixels'''
    row_length = round(math.sqrt(aspect_ratio * image_count))
    return row_length

def resize_to_percent(im: Image, size_percent: int) -> Image:
    '''Resize image to some percent of original'''
    width, height  = im.size
    output_width = int(width * size_percent * 0.01)
    output_height = int(height * size_percent * 0.01)
    im = im.resize((output_width, output_height), Image.BICUBIC)
    return im

@Gooey(show_restart_button=False)
def main():
    files = []
    for format in ['jpg', 'jpeg', 'png', 'bmp', 'gif']:
        files += give_filenames(format)

    default_row_length = calculte_row_length(len(files), aspect_ratio=3/2)

    parser = GooeyParser(description="Program will combine all images in current folder into combined.jpg."
        f"\nThere are {len(files)} images in the folder, suggested row length in custom method is {default_row_length}.")
    parser.add_argument("--method", choices=["vertical", "horizontal", "custom"], default="custom", help="Combine method: vertical, horizontal or custom(rectangular).")
    parser.add_argument('--custom_row_length', type=int, default=default_row_length, help='Only for custom method. Choose how many images are combined in each row.')
    parser.add_argument('--separator_color', default="#000000", help="Separator color, default is #000000.", widget='ColourChooser') 
    parser.add_argument('--separator_width', type=int, default=20, help='Separator width (number of pixels).', widget='Slider')
    parser.add_argument('--quality', type=int, default=95, help='Jpeg output quality, standard is 95', widget='Slider')
    parser.add_argument('--resolution_percent', type=int, default=100, help='Output resolution in % of original image', widget='Slider', gooey_options={'min': 1, 'max': 300})
    parser.add_argument('--version', '-v', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    separator_color = ImageColor.getcolor(args.separator_color, "RGB")

    print('Starting')
    combiner = ImageCombiner(separator_color, args.separator_width)

    if not files:
        print('There are no supported image files in the folder. Press any key.')
        sys.exit()

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
    if args.resolution_percent != 100:
        im_combined = resize_to_percent(im_combined, args.resolution_percent)
    im_combined.save("combined.jpg", quality=args.quality)
    print('Done.\n')

if __name__ == '__main__':
    main()




    