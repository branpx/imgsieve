#!/usr/bin/env python

from __future__ import print_function

from argparse import ArgumentParser
import os
from functools import partial

import imagehash
from PIL import Image


def find_images(directory, recursive=False):
    """Finds all images under the specified directory.

    Args:
        directory: The path to search for images within.
        recursive: A boolean value that determines whether to
            search all subdirectories for images. Defaults to False.

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


def hash_images(image_paths, method='phash', hash_size=8):
    """Hashes images using a specified hashing method.

    Args:
        image_paths: A list of paths to the images to hash.
        method: The image hashing method to use. Defaults to 'phash'.
        hash_size: A base image size to use for hashing. Defaults to 8.

    Returns:
        A tuple containing a dictionary mapping hash values to image
        paths and another dictionary with only the hash values that
        are shared between two or more images.

    """
    if method == 'ahash':
        hash_function = imagehash.average_hash
    elif method == 'phash':
        hash_function = imagehash.phash
    elif method == 'phash_simple':
        hash_function = imagehash.phash_simple
    elif method == 'dhash' or method == 'dhash_horizontal':
        hash_function = imagehash.dhash
    elif method == 'dhash_vertical':
        hash_function = imagehash.dhash_vertical
    elif method == 'whash' or method == 'whash-haar':
        hash_function = imagehash.whash
    elif method == 'whash-db4':
        hash_function = partial(imagehash.whash, mode='db4')
    else:
        raise ValueError('Invalid hashing method: ' + method)

    image_hashes = {}
    duplicates = {}

    for image_path in image_paths:
        with Image.open(image_path) as img:
            image_hash = hash_function(img, hash_size)
        if image_hashes.setdefault(image_hash, []):
            duplicate = duplicates.setdefault(
                str(image_hash), image_hashes[image_hash][:])
            duplicate.append(image_path)
        image_hashes[image_hash].append(image_path)

    return (image_hashes, duplicates)


def filter_duplicates(duplicates, mode='resolution'):
    """Filters out duplicates to keep, according to the filter mode.

    Args:
        duplicates: A list of paths to duplicate/similar images.
        mode: The criteria to filter by. Defaults to 'resolution'.

    Returns:
        The list of duplicates that remain after filtering.

    """
    def resolution(image_path):
        with Image.open(image_path) as img:
            return img.size[0] * img.size[1]

    if mode == 'resolution':
        highest_res = max(duplicates, key=resolution)
        duplicates.remove(highest_res)
    else:
        raise ValueError('Invalid filter mode: ' + mode)

    return duplicates


def main():
    parser = ArgumentParser(prog='imgsieve', usage='%(prog)s [options] path',
                            add_help=False)
    parser.add_argument('-h', '--help', action='help',
                        help='Show this help text and exit.')
    parser.add_argument('path', nargs='?', default=os.getcwd(),
                        help='Path to directory to search for images.'
                        ' Uses cwd if ommited.')
    parser.add_argument('-r', dest='recursive', action='store_true',
                        help='Search for images recursively.')
    parser.add_argument('--filter', dest='filter_mode', default='resolution',
                        help='Criteria to filter by (default: %(default)s).')
    parser.add_argument('--method', default='phash',
                        help='Image hashing method to use'
                        ' (default: %(default)s).')
    parser.add_argument('--size', type=int, default=8,
                        help='Base image size to use for hashing'
                        ' (default: %(default)s).')
    args = parser.parse_args()

    image_paths = find_images(args.path, args.recursive)
    print('Found', len(image_paths), 'images')
    if not image_paths:
        return

    print('Hashing...')
    image_hashes, duplicates = hash_images(image_paths, args.method, args.size)
    print('Found', len(duplicates), 'images with duplicates/similars')
    if not duplicates:
        return
    print('Total of', end=' ')
    print(sum(len(dup_list) for dup_list in duplicates.values()), end=' ')
    print('duplicate/similar image files')

    print('Filtering...')
    trash = []
    for image_hash, paths in duplicates.items():
        trash.append(filter_duplicates(paths[:], args.filter_mode))
    print('Marked', end=' ')
    print(sum(len(image_path) for image_path in trash), end=' ')
    print('image files for deletion', end='')
    if not trash:
        return
    print(':', end=2*'\n')
    for dup_list in trash:
        for duplicate in dup_list:
            print(duplicate)
        print()

    confirm_delete = input('Delete images? (y/n): ')
    if confirm_delete.lstrip().lower().startswith('y'):
        for dup_list in trash:
            for duplicate in dup_list:
                os.remove(duplicate)


if __name__ == '__main__':
    main()
