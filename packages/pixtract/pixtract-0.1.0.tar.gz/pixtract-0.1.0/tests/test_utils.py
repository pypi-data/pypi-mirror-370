import pytest
import numpy as np
import cv2
from pixtract.utils import calculate_sharpness, are_images_duplicates

@pytest.fixture
def dummy_images(tmp_path):
    """Create dummy images for testing."""
    black_image_path = tmp_path / "black.jpg"
    white_image_path = tmp_path / "white.jpg"

    # Create a 10x10 black image
    black_img = np.zeros((10, 10, 3), dtype=np.uint8)
    cv2.imwrite(str(black_image_path), black_img)

    # Create a 10x10 white image
    white_img = np.ones((10, 10, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(white_image_path), white_img)

    return str(black_image_path), str(white_image_path)

def test_calculate_sharpness_on_solid_image(dummy_images):
    """Test that sharpness of a solid color image is 0."""
    black_image_path, _ = dummy_images
    sharpness = calculate_sharpness(black_image_path)
    assert sharpness == 0.0

def test_are_images_duplicates(dummy_images):
    """Test image duplicate function."""
    black_image_path, white_image_path = dummy_images
    # An image should be a duplicate of itself
    assert are_images_duplicates(black_image_path, black_image_path)
    # A black image should not be a duplicate of a white image
    assert not are_images_duplicates(black_image_path, white_image_path)
