"""
Dataset generator for steganography research.

This script automatically generates three types of stego images from cover images:
1. Traditional LSB stego images
2. Random bit-plane stego images
3. Adaptive + random bit-plane stego images

This is useful for creating datasets for steganalysis research.
"""

import os
import cv2
import argparse
from pathlib import Path
from stegano.embed import (
    embed_lsb_traditional,
    embed_random_bitplane,
    embed_adaptive_random
)
from stegano.utils import read_image, validate_image_capacity


def generate_datasets(cover_dir: str,
                     output_base_dir: str = "data",
                     secret_text: str = "This is a secret message for steganography research.",
                     secret_key: int = 12345,
                     min_plane: int = 0,
                     max_plane: int = 2,
                     canny_low: int = 50,
                     canny_high: int = 150):
    """
    Generate all three types of stego images from cover images.
    
    Args:
        cover_dir: Directory containing cover images
        output_base_dir: Base directory for output folders
        secret_text: Secret message to embed in all images
        secret_key: Secret key for random embedding methods
        min_plane: Minimum bit-plane for random embedding
        max_plane: Maximum bit-plane for random embedding
        canny_low: Lower threshold for Canny edge detection
        canny_high: Upper threshold for Canny edge detection
    """
    # Define output directories
    output_dirs = {
        'lsb': os.path.join(output_base_dir, 'stego_lsb'),
        'random': os.path.join(output_base_dir, 'stego_random'),
        'adaptive': os.path.join(output_base_dir, 'stego_adaptive')
    }
    
    # Create output directories if they don't exist
    for dir_path in output_dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    # Get list of image files from cover directory
    cover_path = Path(cover_dir)
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(cover_path.glob(f'*{ext}'))
        image_files.extend(cover_path.glob(f'*{ext.upper()}'))
    
    if not image_files:
        print(f"Warning: No image files found in {cover_dir}")
        return
    
    print(f"Found {len(image_files)} cover images")
    print(f"Secret message length: {len(secret_text)} characters")
    print(f"Secret key: {secret_key}")
    print("-" * 60)
    
    # Process each cover image
    successful = {'lsb': 0, 'random': 0, 'adaptive': 0}
    failed = {'lsb': 0, 'random': 0, 'adaptive': 0}
    
    for img_path in image_files:
        img_name = img_path.name
        print(f"Processing: {img_name}")
        
        try:
            # Validate image capacity
            cover_image = read_image(str(img_path))
            if not validate_image_capacity(cover_image, len(secret_text), 0, max_plane):
                print(f"  Warning: {img_name} has insufficient capacity, skipping...")
                continue
            
            # 1. Generate traditional LSB stego image
            try:
                lsb_output = os.path.join(output_dirs['lsb'], f"lsb_{img_name}")
                embed_lsb_traditional(str(img_path), secret_text, lsb_output)
                successful['lsb'] += 1
                print(f"  ✓ LSB stego created")
            except Exception as e:
                failed['lsb'] += 1
                print(f"  ✗ LSB embedding failed: {e}")
            
            # 2. Generate random bit-plane stego image
            try:
                random_output = os.path.join(output_dirs['random'], f"random_{img_name}")
                embed_random_bitplane(
                    str(img_path), secret_text, secret_key,
                    random_output, min_plane, max_plane
                )
                successful['random'] += 1
                print(f"  ✓ Random bit-plane stego created")
            except Exception as e:
                failed['random'] += 1
                print(f"  ✗ Random embedding failed: {e}")
            
            # 3. Generate adaptive + random bit-plane stego image
            try:
                adaptive_output = os.path.join(output_dirs['adaptive'], f"adaptive_{img_name}")
                embed_adaptive_random(
                    str(img_path), secret_text, secret_key,
                    adaptive_output, canny_low, canny_high
                )
                successful['adaptive'] += 1
                print(f"  ✓ Adaptive stego created")
            except Exception as e:
                failed['adaptive'] += 1
                print(f"  ✗ Adaptive embedding failed: {e}")
        
        except Exception as e:
            print(f"  ✗ Error processing {img_name}: {e}")
        
        print()
    
    # Print summary
    print("=" * 60)
    print("DATASET GENERATION SUMMARY")
    print("=" * 60)
    print(f"Traditional LSB:     {successful['lsb']} successful, {failed['lsb']} failed")
    print(f"Random bit-plane:    {successful['random']} successful, {failed['random']} failed")
    print(f"Adaptive + random:   {successful['adaptive']} successful, {failed['adaptive']} failed")
    print("=" * 60)


def main():
    """Main entry point for dataset generator."""
    parser = argparse.ArgumentParser(
        description='Generate steganography datasets from cover images'
    )
    parser.add_argument(
        '--cover_dir',
        type=str,
        default='data/cover',
        help='Directory containing cover images (default: data/cover)'
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        default='data',
        help='Base output directory (default: data)'
    )
    parser.add_argument(
        '--message',
        type=str,
        default='This is a secret message for steganography research.',
        help='Secret message to embed (default: predefined message)'
    )
    parser.add_argument(
        '--key',
        type=int,
        default=12345,
        help='Secret key for random embedding methods (default: 12345)'
    )
    parser.add_argument(
        '--min_plane',
        type=int,
        default=0,
        help='Minimum bit-plane for random embedding (default: 0)'
    )
    parser.add_argument(
        '--max_plane',
        type=int,
        default=2,
        help='Maximum bit-plane for random embedding (default: 2)'
    )
    parser.add_argument(
        '--canny_low',
        type=int,
        default=50,
        help='Lower threshold for Canny edge detection (default: 50)'
    )
    parser.add_argument(
        '--canny_high',
        type=int,
        default=150,
        help='Upper threshold for Canny edge detection (default: 150)'
    )
    
    args = parser.parse_args()
    
    # Generate datasets
    generate_datasets(
        cover_dir=args.cover_dir,
        output_base_dir=args.output_dir,
        secret_text=args.message,
        secret_key=args.key,
        min_plane=args.min_plane,
        max_plane=args.max_plane,
        canny_low=args.canny_low,
        canny_high=args.canny_high
    )


if __name__ == '__main__':
    main()
