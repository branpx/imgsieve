#!/usr/bin/env python

import os
from functools import partial

import imagehash
from PIL import Image


def find_images(directory, recursive=True):
    """Finds all images under the specified directory.

    Args:
        directory: The path to search for images within.
        recursive: A boolean value that determines whether to
            search all subdirectories for images. Defaults to True.

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
            duplicates.setdefault(str(image_hash), []).append(image_path)
        image_hashes[image_hash].append(image_path)

    return (image_hashes, duplicates)


def main():
    image_paths = find_images(os.path.expanduser('~/Pictures'))
    image_hashes, duplicates = hash_images(image_paths, method='ahash')
    for image_hash, paths in image_hashes.items():
        print(image_hash, '\n', paths, end=2*'\n')
    print(duplicates)


if __name__ == '__main__':
    main()
