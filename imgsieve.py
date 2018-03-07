#!/usr/bin/env python

import os

from PIL import Image


def find_images(directory, recursive=True):
    """Finds all images under the specified directory.

    Args:
        directory: The path to search for images within.

    Returns:
        A list of paths to image files that were found.

    """
    image_paths = []

    for root, _, files in os.walk(directory):
        for file in files:
            if (file.endswith('.jpg') or
                    file.endswith('.jpeg') or
                    file.endswith('.png') or
                    file.endswith('.bmp') or
                    file.endswith('.gif')):
                image_paths.append(os.path.join(root, file))

        if not recursive:
            break

    return image_paths


def main():
    for image_path in find_images(os.path.expanduser('~/Pictures/')):
        print(image_path)


if __name__ == '__main__':
    main()
