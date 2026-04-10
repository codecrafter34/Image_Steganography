# Reliable Detection and Extraction of Image Steganography Using Random and Adaptive Bit-Plane Embedding

## Problem Statement

Traditional Least Significant Bit (LSB) steganography is vulnerable to detection because:
1. **Sequential embedding**: Data is embedded in a predictable order (top-left to bottom-right)
2. **Fixed bit-plane**: Only the 1st LSB is used, making statistical analysis easier
3. **No adaptation**: The method doesn't consider image content characteristics

These limitations make traditional LSB steganography detectable through statistical steganalysis techniques.

## Research Contribution

This project implements an advanced steganography system that addresses these limitations through:

### 1. Random Bit-Plane Embedding
- **Random pixel selection**: Uses a secret key to deterministically select random pixel positions
- **Multiple bit-planes**: Embeds data in randomly selected bit-planes (1st, 2nd, or 3rd LSB)
- **Key-dependent security**: Without the correct secret key, extraction is impossible

### 2. Adaptive Bit-Plane Embedding
- **Edge-aware embedding**: Uses Canny edge detection to classify pixels as edge or smooth regions
- **Adaptive bit-plane selection**:
  - Smooth regions → 1st LSB (least visible)
  - Edge regions → 2nd or 3rd LSB (more robust, less detectable)
- **Content-aware**: Adapts to image characteristics for better security

### 3. Combined Approach
The most advanced method combines both techniques:
- Random pixel order for security
- Adaptive bit-plane selection for robustness
- Key-based deterministic randomness for reproducibility

## Why This Approach Works

### Detection Resistance
- **Random pixel order**: Breaks sequential patterns that steganalyzers look for
- **Multiple bit-planes**: Reduces statistical anomalies in LSB distribution
- **Adaptive selection**: Makes embedding less detectable by matching image content

### Extraction Reliability
- **Deterministic randomness**: Same key always produces the same embedding/extraction sequence
- **Edge-aware selection**: More robust to image processing operations
- **Key-based security**: Only users with the correct key can extract the message

## Project Structure

```
stego_project/
│
├── data/
│   ├── cover/              # Original cover images
│   ├── stego_lsb/          # Traditional LSB stego images
│   ├── stego_random/        # Random bit-plane stego images
│   └── stego_adaptive/     # Adaptive + random stego images
│
├── stegano/
│   ├── utils.py            # Bit-plane utilities and helper functions
│   ├── embed.py            # Embedding logic (3 methods)
│   └── extract.py          # Extraction logic (3 methods)
│
├── dataset_generator.py    # Automated dataset generation
├── test_stego.py          # End-to-end validation script
└── README.md              # This file
```

## Implementation Details

### Core Components

#### 1. Bit-Plane Operations (`utils.py`)
- **Bit extraction**: Get specific bit values from pixel intensities
- **Bit setting**: Modify pixel values at specific bit-planes safely
- **Text conversion**: Convert between text and binary representations
- **Edge detection**: Canny edge detection for adaptive embedding

#### 2. Embedding Methods (`embed.py`)
- **`embed_lsb_traditional()`**: Baseline sequential LSB embedding
- **`embed_random_bitplane()`**: Random pixel order + random bit-planes
- **`embed_adaptive_random()`**: Edge-aware + random embedding (most advanced)

#### 3. Extraction Methods (`extract.py`)
- **`extract_lsb_traditional()`**: Sequential extraction from 1st LSB
- **`extract_random_bitplane()`**: Key-based extraction from random positions
- **`extract_adaptive_random()`**: Key-based adaptive extraction

### Key Features

1. **Deterministic Randomness**
   - Uses Python's `random` module seeded with secret key
   - Same key → same embedding/extraction sequence
   - Different key → different sequence (security)

2. **Adaptive Region Selection**
   - Canny edge detection identifies edge pixels
   - Smooth pixels: embed in 1st LSB (less visible)
   - Edge pixels: embed in 2nd/3rd LSB (more robust)

3. **Safe Pixel Modification**
   - Bit-plane operations prevent overflow (0-255 range)
   - Minimal visual distortion
   - Preserves image quality

## Installation and Setup

### Requirements
```bash
pip install opencv-python numpy matplotlib
```

### Python Version
- Python 3.6 or higher

## Usage

### 1. Basic Embedding and Extraction

```python
from stegano.embed import embed_adaptive_random
from stegano.extract import extract_adaptive_random

# Embed a message
embed_adaptive_random(
    cover_path="data/cover/image.png",
    secret_text="This is a secret message!",
    secret_key=12345,
    output_path="stego_image.png"
)

# Extract the message
message = extract_adaptive_random(
    stego_path="stego_image.png",
    message_length=24,  # Length of "This is a secret message!"
    secret_key=12345
)
print(message)  # Output: "This is a secret message!"
```

### 2. Generate Datasets

```bash
# Place cover images in data/cover/
python dataset_generator.py --cover_dir data/cover --key 12345
```

This will automatically generate:
- Traditional LSB stego images in `data/stego_lsb/`
- Random bit-plane stego images in `data/stego_random/`
- Adaptive stego images in `data/stego_adaptive/`

### 3. Run Validation Tests

```bash
# First, create a test image or place one in data/cover/test_image.png
python test_stego.py
```

This will:
- Test all three embedding/extraction methods
- Verify correct key extraction
- Test wrong key security
- Display pixel difference statistics

## Research Applications

This implementation is designed for:

1. **Steganalysis Research**
   - Generate datasets with different embedding methods
   - Compare detection rates across methods
   - Train ML/CNN models for steganalysis

2. **Security Analysis**
   - Evaluate robustness against statistical attacks
   - Test key-dependent security
   - Analyze visual distortion

3. **Academic Research**
   - Final-year projects
   - Research papers on steganography
   - Comparative studies

## Technical Notes

### Bit-Plane Numbering
- **Plane 0**: 1st LSB (least significant bit)
- **Plane 1**: 2nd LSB
- **Plane 2**: 3rd LSB
- **Plane 7**: MSB (most significant bit)

### Capacity Calculation
- Each character requires 8 bits
- Image capacity = total pixels × available bit-planes
- Example: 512×512 image = 262,144 pixels = 32,768 characters (using 1 bit-plane)

### Edge Detection Parameters
- Default Canny thresholds: low=50, high=150
- Adjustable based on image characteristics
- Must match between embedding and extraction

## Limitations and Future Work

### Current Limitations
- Fixed message length requirement for extraction
- No error correction or compression

### Future Extensions
- Variable-length message encoding
- Error correction codes
- Compression before embedding
- ML-based adaptive bit-plane selection
- Steganalysis detection models

## Citation and References

If you use this code in your research, please cite appropriately. This implementation is based on:
- Random bit-plane steganography principles
- Adaptive embedding based on image content analysis
- Canny edge detection for region classification

## License

This project is provided for educational and research purposes.

## Contact and Support

For questions or issues:
- Review the code comments for detailed explanations
- Check the test script for usage examples
- Ensure all dependencies are installed correctly

---

**Note**: This implementation focuses on the embedding and extraction mechanisms. For steganalysis (detection), you would need to implement statistical analysis or ML-based detection models separately.
