"""
Image steganography embedding module.

This module implements three embedding strategies:
1. Traditional LSB embedding (sequential, 1st LSB only)
2. Random bit-plane embedding (random pixel order, random bit-planes)
3. Adaptive + random bit-plane embedding (edge-aware, random selection)

All methods use a secret key for deterministic randomness.
"""

import cv2
import numpy as np
import random
from typing import Tuple, Optional
from .utils import (
    read_image, get_bit_plane, set_bit_plane,
    text_to_binary, get_edge_mask, validate_image_capacity
)


def _initialize_prng(secret_key: int):
    """
    Initialize pseudo-random number generator with secret key.
    
    This ensures that the same key produces the same random sequence,
    making the embedding process reproducible and key-dependent.
    
    Args:
        secret_key: Integer secret key for PRNG seeding
    """
    random.seed(secret_key)


def _generate_pixel_sequence(image_shape: Tuple[int, int], 
                            num_bits: int, 
                            secret_key: int) -> list:
    """
    Generate a deterministic sequence of pixel coordinates for embedding.
    
    Uses PRNG seeded with secret key to generate random pixel positions.
    The same key will always produce the same sequence.
    
    Args:
        image_shape: Shape of the image (height, width)
        num_bits: Number of bits to embed
        secret_key: Secret key for PRNG
        
    Returns:
        List of (row, col) tuples representing pixel coordinates
    """
    _initialize_prng(secret_key)
    
    height, width = image_shape
    total_pixels = height * width
    
    # Generate random pixel indices without replacement
    # This ensures each pixel is used at most once
    pixel_indices = random.sample(range(total_pixels), min(num_bits, total_pixels))
    
    # Convert linear indices to (row, col) coordinates
    pixel_coords = []
    for idx in pixel_indices:
        row = idx // width
        col = idx % width
        pixel_coords.append((row, col))
    
    return pixel_coords


def _prepare_cover_image_and_capacity_matrix(cover_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load cover image and return:
    - cover image in original format (grayscale or color)
    - 2D capacity matrix used for pixel-coordinate traversal
    """
    cover_image = read_image(cover_path)
    if len(cover_image.shape) == 2:
        return cover_image, cover_image
    if cover_image.shape[2] < 3:
        raise ValueError("Unsupported image format: expected grayscale or 3-channel color image")
    return cover_image, cv2.cvtColor(cover_image, cv2.COLOR_BGR2GRAY)


def _set_pixel_bit(image: np.ndarray, row: int, col: int, bit_value: int, plane: int):
    """
    Set the selected bit-plane in a pixel.
    For color images, uses blue channel (channel 0) to preserve visible color.
    """
    if len(image.shape) == 2:
        image[row, col] = set_bit_plane(image[row, col], plane, bit_value)
    else:
        image[row, col, 0] = set_bit_plane(image[row, col, 0], plane, bit_value)


def embed_lsb_traditional(cover_path: str, 
                         secret_text: str, 
                         output_path: str) -> bool:
    """
    Traditional LSB embedding: sequential pixels, 1st LSB only.
    
    This is the baseline method that embeds data sequentially from top-left
    to bottom-right, using only the least significant bit of each pixel.
    
    Args:
        cover_path: Path to cover image
        secret_text: Secret message to embed
        output_path: Path to save stego image
        
    Returns:
        True if embedding successful, False otherwise
    """
    # Read cover image
    cover_image, capacity_image = _prepare_cover_image_and_capacity_matrix(cover_path)
    stego_image = cover_image.copy()
    
    # Convert text to binary
    binary_message = text_to_binary(secret_text)
    num_bits = len(binary_message)
    
    # Validate capacity
    if not validate_image_capacity(capacity_image, len(secret_text), 0, 0):
        raise ValueError("Image does not have sufficient capacity for the message")
    
    # Embed bits sequentially in 1st LSB
    height, width = capacity_image.shape
    bit_idx = 0
    
    for row in range(height):
        for col in range(width):
            if bit_idx >= num_bits:
                break
            
            # Get current pixel value
            # Get bit to embed
            bit_to_embed = int(binary_message[bit_idx])
            _set_pixel_bit(stego_image, row, col, bit_to_embed, 0)
            
            bit_idx += 1
        
        if bit_idx >= num_bits:
            break
    
    # Save stego image
    cv2.imwrite(output_path, stego_image)
    return True


def embed_random_bitplane(cover_path: str, 
                         secret_text: str, 
                         secret_key: int,
                         output_path: str,
                         min_plane: int = 0,
                         max_plane: int = 2) -> bool:
    """
    Random bit-plane embedding: random pixel order, random bit-plane selection.
    
    This method improves security by:
    - Using random pixel order (instead of sequential)
    - Using random bit-planes (instead of just LSB)
    
    Args:
        cover_path: Path to cover image
        secret_text: Secret message to embed
        secret_key: Secret key for PRNG (determines pixel and plane order)
        output_path: Path to save stego image
        min_plane: Minimum bit-plane to use (default: 0 = LSB)
        max_plane: Maximum bit-plane to use (default: 2 = 3rd LSB)
        
    Returns:
        True if embedding successful, False otherwise
    """
    # Read cover image
    cover_image, capacity_image = _prepare_cover_image_and_capacity_matrix(cover_path)
    stego_image = cover_image.copy()
    
    # Convert text to binary
    binary_message = text_to_binary(secret_text)
    num_bits = len(binary_message)
    
    # Validate capacity
    if not validate_image_capacity(capacity_image, len(secret_text), min_plane, max_plane):
        raise ValueError("Image does not have sufficient capacity for the message")
    
    # Initialize PRNG with secret key
    _initialize_prng(secret_key)
    
    # Generate random pixel sequence
    pixel_coords = _generate_pixel_sequence(capacity_image.shape, num_bits, secret_key)
    
    # Embed bits
    for bit_idx, (row, col) in enumerate(pixel_coords):
        if bit_idx >= num_bits:
            break
        
        # Get current pixel value
        # Get bit to embed
        bit_to_embed = int(binary_message[bit_idx])
        
        # Randomly select bit-plane (deterministic based on key)
        # Use bit_idx as additional seed variation for plane selection
        random.seed(secret_key + bit_idx)
        selected_plane = random.randint(min_plane, max_plane)
        
        _set_pixel_bit(stego_image, row, col, bit_to_embed, selected_plane)
    
    # Save stego image
    cv2.imwrite(output_path, stego_image)
    return True


def embed_adaptive_random(cover_path: str, 
                         secret_text: str, 
                         secret_key: int,
                         output_path: str,
                         canny_low: int = 50,
                         canny_high: int = 150) -> bool:
    """
    Adaptive + random bit-plane embedding: edge-aware with random selection.
    
    This is the most advanced method that:
    - Uses Canny edge detection to classify pixels (edge vs smooth)
    - Embeds in 1st LSB for smooth regions (less visible)
    - Embeds in 2nd or 3rd LSB for edge regions (more robust)
    - Uses random pixel order for security
    
    Args:
        cover_path: Path to cover image
        secret_text: Secret message to embed
        secret_key: Secret key for PRNG
        output_path: Path to save stego image
        canny_low: Lower threshold for Canny edge detection
        canny_high: Upper threshold for Canny edge detection
        
    Returns:
        True if embedding successful, False otherwise
    """
    # Read cover image
    cover_image, capacity_image = _prepare_cover_image_and_capacity_matrix(cover_path)
    stego_image = cover_image.copy()
    
    # Convert text to binary
    binary_message = text_to_binary(secret_text)
    num_bits = len(binary_message)
    
    # Validate capacity
    if not validate_image_capacity(capacity_image, len(secret_text), 0, 2):
        raise ValueError("Image does not have sufficient capacity for the message")
    
    # Generate edge mask
    edge_mask = get_edge_mask(capacity_image, canny_low, canny_high)
    
    # Initialize PRNG with secret key
    _initialize_prng(secret_key)
    
    # Generate random pixel sequence
    pixel_coords = _generate_pixel_sequence(capacity_image.shape, num_bits, secret_key)
    
    # Embed bits with adaptive bit-plane selection
    for bit_idx, (row, col) in enumerate(pixel_coords):
        if bit_idx >= num_bits:
            break
        
        # Get current pixel value
        # Get bit to embed
        bit_to_embed = int(binary_message[bit_idx])
        
        # Adaptive bit-plane selection based on edge classification
        is_edge_pixel = edge_mask[row, col] == 1
        
        if is_edge_pixel:
            # Edge pixel: use 2nd or 3rd LSB (more robust, less visible on edges)
            # Use deterministic random selection based on key and position
            random.seed(secret_key + bit_idx + 1000)  # Offset to vary from pixel sequence
            selected_plane = random.choice([1, 2])  # 2nd or 3rd LSB
        else:
            # Smooth pixel: use 1st LSB (least visible in smooth regions)
            selected_plane = 0
        
        _set_pixel_bit(stego_image, row, col, bit_to_embed, selected_plane)
    
    # Save stego image
    cv2.imwrite(output_path, stego_image)
    return True
