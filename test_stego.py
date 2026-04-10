"""
End-to-end validation script for steganography system.

This script tests all three embedding/extraction methods to ensure:
- Correct message recovery with correct key
- Incorrect output with wrong key
- Pixel difference statistics
- Overall system correctness
"""

import os
import cv2
import numpy as np
from stegano.embed import (
    embed_lsb_traditional,
    embed_random_bitplane,
    embed_adaptive_random
)
from stegano.extract import (
    extract_lsb_traditional,
    extract_random_bitplane,
    extract_adaptive_random
)
from stegano.utils import (
    read_image,
    calculate_pixel_difference
)


def test_traditional_lsb(cover_path: str, test_message: str):
    """
    Test traditional LSB embedding and extraction.
    
    Args:
        cover_path: Path to cover image
        test_message: Test message to embed
    """
    print("=" * 70)
    print("TEST 1: Traditional LSB Embedding/Extraction")
    print("=" * 70)
    
    stego_path = "test_lsb_output.png"
    
    try:
        # Embed message
        print(f"Embedding message: '{test_message}'")
        embed_lsb_traditional(cover_path, test_message, stego_path)
        print("PASS Embedding successful")
        
        # Calculate pixel differences
        cover = read_image(cover_path)
        stego = read_image(stego_path)
        stats = calculate_pixel_difference(cover, stego)
        
        print("\nPixel Difference Statistics:")
        print(f"  Total pixels: {stats['total_pixels']}")
        print(f"  Modified pixels: {stats['modified_pixels']} ({stats['modified_percentage']:.2f}%)")
        print(f"  Max difference: {stats['max_difference']}")
        print(f"  Mean difference: {stats['mean_difference']:.4f}")
        
        # Extract message
        print(f"\nExtracting message...")
        extracted = extract_lsb_traditional(stego_path, len(test_message))
        print(f"Extracted message: '{extracted}'")
        
        # Verify correctness
        if extracted == test_message:
            print("PASS Extraction successful - Message matches!")
        else:
            print("FAIL Extraction failed - Message mismatch!")
            print(f"  Expected length: {len(test_message)}")
            print(f"  Extracted length: {len(extracted)}")
        
        # Cleanup
        if os.path.exists(stego_path):
            os.remove(stego_path)
        
        return extracted == test_message
    
    except Exception as e:
        print(f"FAIL Test failed with error: {e}")
        return False


def test_random_bitplane(cover_path: str, test_message: str, correct_key: int, wrong_key: int):
    """
    Test random bit-plane embedding and extraction.
    
    Args:
        cover_path: Path to cover image
        test_message: Test message to embed
        correct_key: Correct secret key
        wrong_key: Wrong secret key (for testing security)
    """
    print("\n" + "=" * 70)
    print("TEST 2: Random Bit-Plane Embedding/Extraction")
    print("=" * 70)
    
    stego_path = "test_random_output.png"
    
    try:
        # Embed message with correct key
        print(f"Embedding message: '{test_message}'")
        print(f"Using secret key: {correct_key}")
        embed_random_bitplane(cover_path, test_message, correct_key, stego_path)
        print("PASS Embedding successful")
        
        # Calculate pixel differences
        cover = read_image(cover_path)
        stego = read_image(stego_path)
        stats = calculate_pixel_difference(cover, stego)
        
        print("\nPixel Difference Statistics:")
        print(f"  Total pixels: {stats['total_pixels']}")
        print(f"  Modified pixels: {stats['modified_pixels']} ({stats['modified_percentage']:.2f}%)")
        print(f"  Max difference: {stats['max_difference']}")
        print(f"  Mean difference: {stats['mean_difference']:.4f}")
        
        # Extract with correct key
        print(f"\nExtracting with CORRECT key ({correct_key})...")
        extracted_correct = extract_random_bitplane(stego_path, len(test_message), correct_key)
        print(f"Extracted message: '{extracted_correct}'")
        
        if extracted_correct == test_message:
            print("PASS Extraction with correct key successful!")
        else:
            print("FAIL Extraction with correct key failed!")
        
        # Extract with wrong key
        print(f"\nExtracting with WRONG key ({wrong_key})...")
        extracted_wrong = extract_random_bitplane(stego_path, len(test_message), wrong_key)
        print(f"Extracted message: '{extracted_wrong}'")
        
        if extracted_wrong != test_message:
            print("PASS Security test passed - Wrong key produces incorrect output!")
        else:
            print("FAIL Security test failed - Wrong key still produces correct output!")
        
        # Cleanup
        if os.path.exists(stego_path):
            os.remove(stego_path)
        
        return extracted_correct == test_message and extracted_wrong != test_message
    
    except Exception as e:
        print(f"FAIL Test failed with error: {e}")
        return False


def test_adaptive_random(cover_path: str, test_message: str, correct_key: int, wrong_key: int):
    """
    Test adaptive + random bit-plane embedding and extraction.
    
    Args:
        cover_path: Path to cover image
        test_message: Test message to embed
        correct_key: Correct secret key
        wrong_key: Wrong secret key (for testing security)
    """
    print("\n" + "=" * 70)
    print("TEST 3: Adaptive + Random Bit-Plane Embedding/Extraction")
    print("=" * 70)
    
    stego_path = "test_adaptive_output.png"
    
    try:
        # Embed message with correct key
        print(f"Embedding message: '{test_message}'")
        print(f"Using secret key: {correct_key}")
        embed_adaptive_random(cover_path, test_message, correct_key, stego_path)
        print("PASS Embedding successful")
        
        # Calculate pixel differences
        cover = read_image(cover_path)
        stego = read_image(stego_path)
        stats = calculate_pixel_difference(cover, stego)
        
        print("\nPixel Difference Statistics:")
        print(f"  Total pixels: {stats['total_pixels']}")
        print(f"  Modified pixels: {stats['modified_pixels']} ({stats['modified_percentage']:.2f}%)")
        print(f"  Max difference: {stats['max_difference']}")
        print(f"  Mean difference: {stats['mean_difference']:.4f}")
        
        # Extract with correct key
        print(f"\nExtracting with CORRECT key ({correct_key})...")
        extracted_correct = extract_adaptive_random(stego_path, len(test_message), correct_key)
        print(f"Extracted message: '{extracted_correct}'")
        
        if extracted_correct == test_message:
            print("PASS Extraction with correct key successful!")
        else:
            print("FAIL Extraction with correct key failed!")
        
        # Extract with wrong key
        print(f"\nExtracting with WRONG key ({wrong_key})...")
        extracted_wrong = extract_adaptive_random(stego_path, len(test_message), wrong_key)
        print(f"Extracted message: '{extracted_wrong}'")
        
        if extracted_wrong != test_message:
            print("PASS Security test passed - Wrong key produces incorrect output!")
        else:
            print("FAIL Security test failed - Wrong key still produces correct output!")
        
        # Cleanup
        if os.path.exists(stego_path):
            os.remove(stego_path)
        
        return extracted_correct == test_message and extracted_wrong != test_message
    
    except Exception as e:
        print(f"FAIL Test failed with error: {e}")
        return False


def main():
    """Run all validation tests."""
    print("\n" + "=" * 70)
    print("STEGANOGRAPHY SYSTEM VALIDATION")
    print("=" * 70)
    
    # Test parameters
    cover_path = "data/cover/example_image.png"  # User should provide a test image
    test_message = "Hello, this is a secret message! 123"
    correct_key = 12345
    wrong_key = 99999
    
    # Check if cover image exists
    if not os.path.exists(cover_path):
        print(f"\nError: Cover image not found at {cover_path}")
        print("Please provide a test image or update the cover_path variable.")
        print("\nYou can create a test image using OpenCV:")
        print("  import cv2")
        print("  import numpy as np")
        print("  test_img = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)")
        print("  cv2.imwrite('data/cover/test_image.png', test_img)")
        return
    
    # Run tests
    results = {}
    
    results['lsb'] = test_traditional_lsb(cover_path, test_message)
    results['random'] = test_random_bitplane(cover_path, test_message, correct_key, wrong_key)
    results['adaptive'] = test_adaptive_random(cover_path, test_message, correct_key, wrong_key)
    
    # Print final summary
    print("\n" + "=" * 70)
    print("FINAL TEST SUMMARY")
    print("=" * 70)
    print(f"Traditional LSB:        {'PASS' if results['lsb'] else 'FAIL'}")
    print(f"Random bit-plane:       {'PASS' if results['random'] else 'FAIL'}")
    print(f"Adaptive + random:      {'PASS' if results['adaptive'] else 'FAIL'}")
    print("=" * 70)
    
    if all(results.values()):
        print("\nAll tests passed! System is working correctly.")
    else:
        print("\nSome tests failed. Please review the errors above.")


if __name__ == '__main__':
    main()
