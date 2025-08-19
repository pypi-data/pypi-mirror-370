"""Utility functions for image processing."""

import cv2
import logging
from skimage.metrics import structural_similarity as ssim

def calculate_sharpness(image_path: str) -> float:
    """
    Calculates the sharpness of an image using the variance of the Laplacian.

    Args:
        image_path (str): The path to the image file.

    Returns:
        float: The sharpness value. A higher value indicates a sharper image.
    """
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            logging.warning(f"Could not read image for sharpness calculation: {image_path}")
            return 0.0 # Return float for consistency
        return float(cv2.Laplacian(image, cv2.CV_64F).var()) # Ensure float return
    except cv2.error as e:
        logging.error(f"OpenCV error calculating sharpness for {image_path}: {e}", exc_info=True)
        return 0.0
    except Exception as e:
        logging.error(f"Unexpected error calculating sharpness for {image_path}: {e}", exc_info=True)
        return 0.0

def are_images_duplicates(image_path1: str, image_path2: str, duplicate_threshold: float = 1.0) -> bool:
    """
    Compares two images for similarity to determine if they are duplicates.

    Args:
        image_path1 (str): The path to the first image file.
        image_path2 (str): The path to the second image file.
        duplicate_threshold (float, optional): The threshold for similarity. Higher values (closer to 1.0) mean images must be nearly identical to be considered duplicates. Defaults to 1.0.

    Returns:
        bool: True if the images are considered duplicates, False otherwise.
    """
    try:
        image1 = cv2.imread(image_path1)
        image2 = cv2.imread(image_path2)

        if image1 is None:
            logging.warning(f"Could not read first image for duplicate comparison: {image_path1}")
            return False
        if image2 is None:
            logging.warning(f"Could not read second image for duplicate comparison: {image_path2}")
            return False

        # Ensure images are of the same size for SSIM calculation
        # Resize to a common size if they are not already
        if image1.shape != image2.shape:
            image1 = cv2.resize(image1, (256, 256))
            image2 = cv2.resize(image2, (256, 256))

        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

        similarity_index, _ = ssim(gray1, gray2, full=True)
        return similarity_index >= duplicate_threshold
    except cv2.error as e:
        logging.error(f"OpenCV error comparing images {image_path1} and {image_path2}: {e}", exc_info=True)
        return False
    except Exception as e:
        logging.error(f"Unexpected error comparing images {image_path1} and {image_path2}: {e}", exc_info=True)
        return False