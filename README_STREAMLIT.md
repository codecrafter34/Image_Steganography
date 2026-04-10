# 🔐 Steganography System - Streamlit UI

A modern, interactive web application for hiding and extracting secret messages in images using advanced steganography techniques.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## ✨ Features

### 🎨 Modern UI
- Beautiful gradient design with purple/blue theme
- Responsive layout
- Interactive components with smooth animations
- Professional, clean interface

### 🔒 Embedding
- Upload cover images (PNG, JPG, JPEG, BMP)
- Enter secret messages
- Choose from 3 algorithms:
  - **Traditional LSB**: Fast and simple
  - **Random Bit-Plane**: Enhanced security with random selection
  - **Adaptive + Random**: Most secure, uses edge detection
- Set secret keys for encryption
- View before/after comparison
- Download stego images

### 🔓 Extraction
- Upload stego images
- Select matching algorithm
- Enter secret key (if used)
- Extract hidden messages
- View extraction statistics

### 📊 Statistics
- Real-time pixel modification analysis
- Stealth quality indicators
- Side-by-side image comparison
- Detailed metrics display

## 📁 Project Structure

```
stego_project/
├── app.py                  # Streamlit web application
├── stegano/
│   ├── embed.py           # Embedding algorithms
│   ├── extract.py         # Extraction algorithms
│   └── utils.py           # Utility functions
├── example_usage.py       # Command-line examples
├── test_stego.py          # Automated tests
└── requirements.txt       # Dependencies
```

## 🧪 Testing

```bash
# Run automated tests
python test_stego.py

# Run command-line examples
python example_usage.py
```

## 🔑 Usage Tips

1. **Remember your secret key** - Required for Random Bit-Plane and Adaptive methods
2. **Use larger images** for longer messages
3. **Match extraction settings** with embedding settings
4. **PNG format recommended** for lossless storage

## 📝 Algorithms

### Traditional LSB
- Embeds data sequentially in the least significant bit
- Fast and simple
- Good for basic steganography

### Random Bit-Plane
- Uses random pixel selection
- Embeds in multiple bit planes (0-2)
- Requires secret key
- Enhanced security

### Adaptive + Random
- Uses Canny edge detection
- Adaptive bit-plane selection based on image features
- Most secure option
- Requires secret key

## 🛠️ Requirements

- Python 3.7+
- OpenCV
- NumPy
- Pillow
- Streamlit

## 📄 License

This project is for educational purposes.
