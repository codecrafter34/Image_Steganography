"""
Bit-plane utilities for image steganography operations.

This module provides core functions for:
- Reading and processing grayscale or color images
- Bit-plane manipulation (extracting and setting bits)
- Text-to-binary and binary-to-text conversion
- Safe pixel value modification to prevent overflow
"""

import cv2
import numpy as np
from typing import Tuple


# ------------------------------------------------------------------
# IMAGE UTILITIES
# ------------------------------------------------------------------

def read_image(image_path: str) -> np.ndarray:
    """
    Read an image while preserving its original channel format.
    """
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"Could not read image from {image_path}")
    return img


def read_grayscale_image(image_path: str) -> np.ndarray:
    """
    Read an image and convert it to grayscale.
    """
    img = read_image(image_path)
    if len(img.shape) == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# ------------------------------------------------------------------
# BIT-PLANE OPERATIONS
# ------------------------------------------------------------------

def get_bit_plane(pixel_value: int, plane: int) -> int:
    """
    Extract a specific bit-plane from a pixel value.
    """
    if not (0 <= plane <= 7):
        raise ValueError(f"Bit-plane must be between 0 and 7, got {plane}")

    return (int(pixel_value) >> plane) & 1


def set_bit_plane(pixel_value: int, plane: int, bit_value: int) -> int:
    """
    Safely set a specific bit-plane in a pixel value.

    FIXED:
    - Prevents uint8 overflow
    - Ensures 8-bit masking
    """
    if not (0 <= plane <= 7):
        raise ValueError(f"Bit-plane must be between 0 and 7, got {plane}")

    if bit_value not in (0, 1):
        raise ValueError(f"Bit value must be 0 or 1, got {bit_value}")

    # Convert to Python int (VERY IMPORTANT)
    pixel_value = int(pixel_value)

    # Clear target bit safely (8-bit mask)
    mask = ~(1 << plane) & 0xFF   # 🔥 FIX
    pixel_value = pixel_value & mask

    # Set new bit
    pixel_value |= (bit_value << plane)

    # Return as normal int (cv2 will convert later)
    return pixel_value


# ------------------------------------------------------------------
# TEXT ↔ BINARY CONVERSION
# ------------------------------------------------------------------

def text_to_binary(text: str) -> str:
    """
    Convert text string to binary (UTF-8).
    """
    text_bytes = text.encode('utf-8')
    return ''.join(format(byte, '08b') for byte in text_bytes)


def binary_to_text(binary_string: str) -> str:
    """
    Convert binary string back to text (UTF-8).
    """
    if len(binary_string) % 8 != 0:
        raise ValueError(
            f"Binary string length must be a multiple of 8, got {len(binary_string)}"
        )

    byte_values = [
        int(binary_string[i:i + 8], 2)
        for i in range(0, len(binary_string), 8)
    ]

    decoded = bytes(byte_values).decode('utf-8', errors='replace')
    # Ensure ensuring ASCII output to prevent console crashes on Windows
    return decoded.encode('ascii', errors='replace').decode('ascii')


# ------------------------------------------------------------------
# EDGE DETECTION (FOR ADAPTIVE STEGO)
# ------------------------------------------------------------------

def get_edge_mask(image: np.ndarray,
                  low_threshold: int = 50,
                  high_threshold: int = 150) -> np.ndarray:
    """
    Generate a binary edge mask using Canny edge detection.
    """
    # Convert to grayscale for edge detection if image is color.
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Preprocess: Mask out lower 3 bits (planes 0-2) to make edge detection
    # robust against the embedding changes. This ensures the mask is 
    # identical for both cover and stego images.
    start_mask_img = image & 0xF8
    edges = cv2.Canny(start_mask_img, low_threshold, high_threshold)
    return (edges > 0).astype(np.uint8)


# ------------------------------------------------------------------
# IMAGE QUALITY METRICS
# ------------------------------------------------------------------

def calculate_pixel_difference(cover: np.ndarray, stego: np.ndarray) -> dict:
    """
    Calculate statistics about pixel differences.
    """
    if cover.shape != stego.shape:
        raise ValueError("Cover and stego images must have the same dimensions")

    diff = np.abs(cover.astype(int) - stego.astype(int))
    if len(diff.shape) == 3:
        modified_mask = np.any(diff > 0, axis=2)
        total_pixels = cover.shape[0] * cover.shape[1]
    else:
        modified_mask = diff > 0
        total_pixels = cover.size
    modified_pixels = int(np.sum(modified_mask))

    return {
        'total_pixels': int(total_pixels),
        'modified_pixels': modified_pixels,
        'max_difference': int(np.max(diff)),
        'mean_difference': float(np.mean(diff)),
        'modified_percentage': float(modified_pixels / total_pixels * 100)
    }


# ------------------------------------------------------------------
# CAPACITY CHECK
# ------------------------------------------------------------------

def validate_image_capacity(image: np.ndarray,
                            message_length: int,
                            min_plane: int = 0,
                            max_plane: int = 2) -> bool:
    """
    Validate if an image has sufficient capacity to embed a message.
    """
    required_bits = message_length * 8
    if len(image.shape) == 3:
        available_pixels = image.shape[0] * image.shape[1]
    else:
        available_pixels = image.size
    return available_pixels >= required_bits
