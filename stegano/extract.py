"""
Image steganography extraction module.

This module implements extraction logic for all three embedding methods.
Extraction must use the SAME secret key and logic as embedding to recover
the hidden message correctly.
"""

import cv2
import numpy as np
import random
from typing import Optional
from .utils import (
    read_image, get_bit_plane, binary_to_text, get_edge_mask
)


def _initialize_prng(secret_key: int):
    """
    Initialize pseudo-random number generator with secret key.
    
    This must match the PRNG initialization in embed.py exactly.
    
    Args:
        secret_key: Integer secret key for PRNG seeding
    """
    random.seed(secret_key)


def _generate_pixel_sequence(image_shape: tuple, 
                            num_bits: int, 
                            secret_key: int) -> list:
    """
    Generate the same deterministic pixel sequence used during embedding.
    
    This function must produce the EXACT same sequence as in embed.py.
    
    Args:
        image_shape: Shape of the image (height, width)
        num_bits: Number of bits to extract
        secret_key: Secret key for PRNG (must match embedding key)
        
    Returns:
        List of (row, col) tuples representing pixel coordinates
    """
    _initialize_prng(secret_key)
    
    height, width = image_shape
    total_pixels = height * width
    
    # Generate random pixel indices without replacement
    pixel_indices = random.sample(range(total_pixels), min(num_bits, total_pixels))
    
    # Convert linear indices to (row, col) coordinates
    pixel_coords = []
    for idx in pixel_indices:
        row = idx // width
        col = idx % width
        pixel_coords.append((row, col))
    
    return pixel_coords


def _prepare_stego_image_and_capacity_matrix(stego_path: str):
    """
    Load stego image and return:
    - stego image in original format (grayscale or color)
    - 2D capacity matrix used for pixel-coordinate traversal
    """
    stego_image = read_image(stego_path)
    if len(stego_image.shape) == 2:
        return stego_image, stego_image
    if stego_image.shape[2] < 3:
        raise ValueError("Unsupported image format: expected grayscale or 3-channel color image")
    return stego_image, cv2.cvtColor(stego_image, cv2.COLOR_BGR2GRAY)


def _get_pixel_bit_source(image, row: int, col: int) -> int:
    """
    Return pixel value used for bit extraction.
    For color images, extraction reads from blue channel (channel 0),
    matching embed.py.
    """
    if len(image.shape) == 2:
        return int(image[row, col])
    return int(image[row, col, 0])


def extract_lsb_traditional(stego_path: str, 
                           message_length: int) -> str:
    """
    Extract message from traditional LSB stego image.
    
    This method extracts bits sequentially from the 1st LSB of pixels,
    matching the sequential embedding order.
    
    Args:
        stego_path: Path to stego image
        message_length: Length of the hidden message in characters
        
    Returns:
        Extracted secret message
    """
    # Read stego image
    stego_image, capacity_image = _prepare_stego_image_and_capacity_matrix(stego_path)
    
    # Calculate number of bits to extract
    num_bits = message_length * 8
    
    # Extract bits sequentially from 1st LSB
    height, width = capacity_image.shape
    binary_message = []
    bit_idx = 0
    
    for row in range(height):
        for col in range(width):
            if bit_idx >= num_bits:
                break
            
            # Get pixel value
            pixel_value = _get_pixel_bit_source(stego_image, row, col)
            
            # Extract 1st LSB (plane 0)
            bit = get_bit_plane(pixel_value, 0)
            binary_message.append(str(bit))
            
            bit_idx += 1
        
        if bit_idx >= num_bits:
            break
    
    # Convert binary to text
    binary_string = ''.join(binary_message)
    message = binary_to_text(binary_string)
    
    return message


def extract_random_bitplane(stego_path: str, 
                           message_length: int,
                           secret_key: int,
                           min_plane: int = 0,
                           max_plane: int = 2) -> str:
    """
    Extract message from random bit-plane stego image.
    
    This method must use the SAME secret key and random sequence as embedding
    to correctly recover the message.
    
    Args:
        stego_path: Path to stego image
        message_length: Length of the hidden message in characters
        secret_key: Secret key for PRNG (must match embedding key)
        min_plane: Minimum bit-plane used during embedding
        max_plane: Maximum bit-plane used during embedding
        
    Returns:
        Extracted secret message
    """
    # Read stego image
    stego_image, capacity_image = _prepare_stego_image_and_capacity_matrix(stego_path)
    
    # Calculate number of bits to extract
    num_bits = message_length * 8
    
    # Initialize PRNG with secret key
    _initialize_prng(secret_key)
    
    # Generate the same random pixel sequence used during embedding
    pixel_coords = _generate_pixel_sequence(capacity_image.shape, num_bits, secret_key)
    
    # Extract bits
    binary_message = []
    for bit_idx, (row, col) in enumerate(pixel_coords):
        if bit_idx >= num_bits:
            break
        
        # Get pixel value
        pixel_value = _get_pixel_bit_source(stego_image, row, col)
        
        # Reconstruct the same random bit-plane selection as embedding
        # This must match embed_random_bitplane() exactly
        random.seed(secret_key + bit_idx)
        selected_plane = random.randint(min_plane, max_plane)
        
        # Extract bit from the selected plane
        bit = get_bit_plane(pixel_value, selected_plane)
        binary_message.append(str(bit))
    
    # Convert binary to text
    binary_string = ''.join(binary_message)
    message = binary_to_text(binary_string)
    
    return message


def extract_adaptive_random(stego_path: str, 
                           message_length: int,
                           secret_key: int,
                           canny_low: int = 50,
                           canny_high: int = 150) -> str:
    """
    Extract message from adaptive + random bit-plane stego image.
    
    This method must:
    - Use the SAME secret key as embedding
    - Generate the SAME edge mask (using same Canny parameters)
    - Use the SAME pixel sequence and bit-plane selection logic
    
    Args:
        stego_path: Path to stego image
        message_length: Length of the hidden message in characters
        secret_key: Secret key for PRNG (must match embedding key)
        canny_low: Lower threshold for Canny edge detection (must match embedding)
        canny_high: Upper threshold for Canny edge detection (must match embedding)
        
    Returns:
        Extracted secret message
    """
    # Read stego image
    stego_image, capacity_image = _prepare_stego_image_and_capacity_matrix(stego_path)
    
    # Calculate number of bits to extract
    num_bits = message_length * 8
    
    # Generate the SAME edge mask as during embedding
    # Note: We use the stego image, but edge detection should be similar
    # In practice, you might want to use the original cover image if available
    # For extraction, we'll use the stego image (edges should be similar)
    edge_mask = get_edge_mask(capacity_image, canny_low, canny_high)
    
    # Initialize PRNG with secret key
    _initialize_prng(secret_key)
    
    # Generate the same random pixel sequence used during embedding
    pixel_coords = _generate_pixel_sequence(capacity_image.shape, num_bits, secret_key)
    
    # Extract bits with adaptive bit-plane selection
    binary_message = []
    for bit_idx, (row, col) in enumerate(pixel_coords):
        if bit_idx >= num_bits:
            break
        
        # Get pixel value
        pixel_value = _get_pixel_bit_source(stego_image, row, col)
        
        # Reconstruct the same adaptive bit-plane selection as embedding
        is_edge_pixel = edge_mask[row, col] == 1
        
        if is_edge_pixel:
            # Edge pixel: extract from 2nd or 3rd LSB
            # Must match the exact same random selection as embedding
            random.seed(secret_key + bit_idx + 1000)  # Same offset as embedding
            selected_plane = random.choice([1, 2])
        else:
            # Smooth pixel: extract from 1st LSB
            selected_plane = 0
        
        # Extract bit from the selected plane
        bit = get_bit_plane(pixel_value, selected_plane)
        binary_message.append(str(bit))
    
    # Convert binary to text
    binary_string = ''.join(binary_message)
    message = binary_to_text(binary_string)
    
    return message
