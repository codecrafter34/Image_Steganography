"""
Simple example demonstrating how to use the steganography system.

This script shows basic embedding and extraction operations.
"""

import cv2
import numpy as np
import os
from stegano.embed import embed_adaptive_random, embed_random_bitplane, embed_lsb_traditional
from stegano.extract import extract_adaptive_random, extract_random_bitplane, extract_lsb_traditional
from stegano.utils import calculate_pixel_difference, read_image


def create_test_image(output_path: str, size: tuple = (512, 512)):
    """
    Create a test color image for demonstration.
    
    Args:
        output_path: Path to save the test image
        size: Image dimensions (height, width)
    """
    # Create a color test image with some patterns
    height, width = size
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add some patterns to make it interesting
    for i in range(0, height, 50):
        img[i:i+25, :, 0] = 128  # Blue stripes
    
    for j in range(0, width, 50):
        img[:, j:j+25, 1] = 200  # Green stripes
    
    # Add some random noise
    noise = np.random.randint(0, 50, (height, width, 3), dtype=np.uint8)
    img = np.clip(img.astype(int) + noise, 0, 255).astype(np.uint8)
    
    # Save image
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    cv2.imwrite(output_path, img)
    print(f"Created test image: {output_path}")


def main():
    """Run example demonstrations."""
    print("=" * 70)
    print("STEGANOGRAPHY SYSTEM - EXAMPLE USAGE")
    print("=" * 70)
    
    # Create test image if it doesn't exist
    cover_path = "data/cover/example_image.png"
    if not os.path.exists(cover_path):
        print("\nCreating test image...")
        create_test_image(cover_path)
    
    # Test message
    secret_message = "Hello from steganography! This is a secret message."
    secret_key = 12345
    
    print(f"\nSecret message: '{secret_message}'")
    print(f"Message length: {len(secret_message)} characters")
    print(f"Secret key: {secret_key}")
    
    # Example 1: Traditional LSB
    print("\n" + "-" * 70)
    print("Example 1: Traditional LSB Embedding")
    print("-" * 70)
    
    stego_lsb_path = "example_lsb.png"
    embed_lsb_traditional(cover_path, secret_message, stego_lsb_path)
    extracted_lsb = extract_lsb_traditional(stego_lsb_path, len(secret_message))
    
    print(f"Original:  '{secret_message}'")
    print(f"Extracted: '{extracted_lsb}'")
    print(f"Match: {secret_message == extracted_lsb}")
    
    # Calculate differences
    cover = read_image(cover_path)
    stego = read_image(stego_lsb_path)
    stats = calculate_pixel_difference(cover, stego)
    print(f"Modified pixels: {stats['modified_pixels']} ({stats['modified_percentage']:.2f}%)")
    
    # Example 2: Random Bit-Plane
    print("\n" + "-" * 70)
    print("Example 2: Random Bit-Plane Embedding")
    print("-" * 70)
    
    stego_random_path = "example_random.png"
    embed_random_bitplane(cover_path, secret_message, secret_key, stego_random_path)
    extracted_random = extract_random_bitplane(stego_random_path, len(secret_message), secret_key)
    
    print(f"Original:  '{secret_message}'")
    print(f"Extracted: '{extracted_random}'")
    print(f"Match: {secret_message == extracted_random}")
    
    # Test with wrong key
    wrong_key = 99999
    extracted_wrong = extract_random_bitplane(stego_random_path, len(secret_message), wrong_key)
    print(f"Wrong key extraction: '{extracted_wrong}'")
    print(f"Security test: {extracted_wrong != secret_message}")
    
    # Example 3: Adaptive + Random
    print("\n" + "-" * 70)
    print("Example 3: Adaptive + Random Bit-Plane Embedding")
    print("-" * 70)
    
    stego_adaptive_path = "example_adaptive.png"
    embed_adaptive_random(cover_path, secret_message, secret_key, stego_adaptive_path)
    extracted_adaptive = extract_adaptive_random(stego_adaptive_path, len(secret_message), secret_key)
    
    print(f"Original:  '{secret_message}'")
    print(f"Extracted: '{extracted_adaptive}'")
    print(f"Match: {secret_message == extracted_adaptive}")
    
    # Test with wrong key
    extracted_wrong_adaptive = extract_adaptive_random(stego_adaptive_path, len(secret_message), wrong_key)
    print(f"Wrong key extraction: '{extracted_wrong_adaptive}'")
    print(f"Security test: {extracted_wrong_adaptive != secret_message}")
    
    # Calculate differences
    stego_adaptive = read_image(stego_adaptive_path)
    stats_adaptive = calculate_pixel_difference(cover, stego_adaptive)
    print(f"Modified pixels: {stats_adaptive['modified_pixels']} ({stats_adaptive['modified_percentage']:.2f}%)")
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)
    print("\nGenerated files:")
    print(f"  - {stego_lsb_path}")
    print(f"  - {stego_random_path}")
    print(f"  - {stego_adaptive_path}")
    print("\nYou can compare these stego images with the original cover image.")


if __name__ == '__main__':
    main()
