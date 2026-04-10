"""
Interactive Streamlit UI for Image Steganography System

This application provides a modern, user-friendly interface for:
- Embedding secret messages into images
- Extracting hidden messages from stego images
- Comparing cover and stego images
- Viewing statistics and analysis
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import os
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
    calculate_pixel_difference,
    read_image
)

# Page configuration
st.set_page_config(
    page_title="Steganography System",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background: white;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    h1 {
        color: #667eea;
        font-weight: 700;
    }
    h2, h3 {
        color: #764ba2;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    </style>
""", unsafe_allow_html=True)


def save_uploaded_file(uploaded_file, prefix="temp"):
    """Save uploaded file temporarily and return path"""
    if uploaded_file is not None:
        file_path = f"{prefix}_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None


def pil_to_cv2(pil_image):
    """Convert PIL Image to OpenCV format"""
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2GRAY)


def cv2_to_pil(cv2_image):
    """Convert OpenCV image to PIL format"""
    return Image.fromarray(cv2_image)


def display_image_comparison(col1, col2, cover_path, stego_path, title1="Cover Image", title2="Stego Image"):
    """Display side-by-side image comparison"""
    with col1:
        st.subheader(title1)
        cover_img = Image.open(cover_path)
        st.image(cover_img, use_container_width=True)
    
    with col2:
        st.subheader(title2)
        stego_img = Image.open(stego_path)
        st.image(stego_img, use_container_width=True)


def display_statistics(cover_path, stego_path):
    """Display detailed statistics about the steganography operation"""
    cover = read_image(cover_path)
    stego = read_image(stego_path)
    stats = calculate_pixel_difference(cover, stego)
    
    st.markdown("### 📊 Image Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Pixels",
            value=f"{stats['total_pixels']:,}"
        )
    
    with col2:
        st.metric(
            label="Modified Pixels",
            value=f"{stats['modified_pixels']:,}",
            delta=f"{stats['modified_percentage']:.3f}%"
        )
    
    with col3:
        st.metric(
            label="Max Difference",
            value=stats['max_difference']
        )
    
    with col4:
        st.metric(
            label="Mean Difference",
            value=f"{stats['mean_difference']:.4f}"
        )
    
    # Visual indicator
    if stats['modified_percentage'] < 0.1:
        st.markdown('<div class="success-box">✅ Excellent stealth! Very low modification rate.</div>', unsafe_allow_html=True)
    elif stats['modified_percentage'] < 1.0:
        st.markdown('<div class="info-box">ℹ️ Good stealth. Modifications are minimal.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="warning-box">⚠️ Higher modification rate. Consider using a larger image.</div>', unsafe_allow_html=True)


def main():
    # Header
    st.markdown("<h1 style='text-align: center;'>🔐 Advanced Image Steganography System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.2em;'>Hide secret messages in images with military-grade security</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/security-lock.png", width=80)
        st.title("⚙️ Settings")
        
        mode = st.radio(
            "Select Mode",
            ["🔒 Embed Message", "🔓 Extract Message"],
            help="Choose whether to hide a message or reveal a hidden one"
        )
        
        st.markdown("---")
        
        if mode == "🔒 Embed Message":
            st.subheader("Embedding Method")
            method = st.selectbox(
                "Algorithm",
                [
                    "Traditional LSB",
                    "Random Bit-Plane",
                    "Adaptive + Random"
                ],
                help="Choose the steganography algorithm"
            )
            
            if method != "Traditional LSB":
                secret_key = st.number_input(
                    "Secret Key",
                    min_value=1,
                    max_value=999999,
                    value=12345,
                    help="Remember this key for extraction!"
                )
            else:
                secret_key = None
            
            st.markdown("---")
            st.markdown("### 📖 Method Info")
            
            if method == "Traditional LSB":
                st.info("**Traditional LSB**: Simple and fast. Embeds data sequentially in the least significant bit.")
            elif method == "Random Bit-Plane":
                st.info("**Random Bit-Plane**: Enhanced security using random pixel selection and multiple bit planes.")
            else:
                st.info("**Adaptive + Random**: Most secure. Uses edge detection to adaptively select bit planes.")
        
        else:  # Extract mode
            st.subheader("Extraction Method")
            method = st.selectbox(
                "Algorithm",
                [
                    "Traditional LSB",
                    "Random Bit-Plane",
                    "Adaptive + Random"
                ]
            )
            
            if method != "Traditional LSB":
                secret_key = st.number_input(
                    "Secret Key",
                    min_value=1,
                    max_value=999999,
                    value=12345,
                    help="Enter the key used during embedding"
                )
            else:
                secret_key = None
            
            message_length = st.number_input(
                "Message Length (characters)",
                min_value=1,
                max_value=10000,
                value=50,
                help="Approximate length of the hidden message"
            )
    
    # Main content area
    if mode == "🔒 Embed Message":
        st.header("🔒 Embed Secret Message")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📤 Upload Cover Image")
            cover_file = st.file_uploader(
                "Choose a grayscale or color image",
                type=["png", "jpg", "jpeg", "bmp"],
                key="cover"
            )
            
            if cover_file:
                st.image(cover_file, caption="Cover Image", use_container_width=True)
        
        with col2:
            st.subheader("✍️ Secret Message")
            secret_message = st.text_area(
                "Enter your secret message",
                height=150,
                placeholder="Type your confidential message here...",
                help="This message will be hidden in the image"
            )
            
            if secret_message:
                st.info(f"📝 Message length: {len(secret_message)} characters")
        
        st.markdown("---")
        
        if st.button("🚀 Embed Message", use_container_width=True):
            if not cover_file:
                st.error("❌ Please upload a cover image!")
            elif not secret_message:
                st.error("❌ Please enter a secret message!")
            else:
                with st.spinner("🔄 Embedding message... Please wait..."):
                    try:
                        # Save uploaded file
                        cover_path = save_uploaded_file(cover_file, "cover")
                        stego_path = "stego_output.png"
                        
                        # Perform embedding
                        if method == "Traditional LSB":
                            embed_lsb_traditional(cover_path, secret_message, stego_path)
                        elif method == "Random Bit-Plane":
                            embed_random_bitplane(cover_path, secret_message, secret_key, stego_path)
                        else:  # Adaptive + Random
                            embed_adaptive_random(cover_path, secret_message, secret_key, stego_path)
                        
                        st.success("✅ Message embedded successfully!")
                        
                        # Display results
                        st.markdown("---")
                        st.header("📊 Results")
                        
                        # Image comparison
                        col1, col2 = st.columns(2)
                        display_image_comparison(col1, col2, cover_path, stego_path)
                        
                        # Statistics
                        display_statistics(cover_path, stego_path)
                        
                        # Download button
                        st.markdown("---")
                        with open(stego_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download Stego Image",
                                data=file,
                                file_name="stego_image.png",
                                mime="image/png",
                                use_container_width=True
                            )
                        
                        # Cleanup
                        if os.path.exists(cover_path):
                            os.remove(cover_path)
                    
                    except Exception as e:
                        st.error(f"❌ Error during embedding: {str(e)}")
    
    else:  # Extract mode
        st.header("🔓 Extract Hidden Message")
        
        st.subheader("📤 Upload Stego Image")
        stego_file = st.file_uploader(
            "Choose the image containing the hidden message",
            type=["png", "jpg", "jpeg", "bmp"],
            key="stego"
        )
        
        if stego_file:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.image(stego_file, caption="Stego Image", use_container_width=True)
        
        st.markdown("---")
        
        if st.button("🔍 Extract Message", use_container_width=True):
            if not stego_file:
                st.error("❌ Please upload a stego image!")
            else:
                with st.spinner("🔄 Extracting message... Please wait..."):
                    try:
                        # Save uploaded file
                        stego_path = save_uploaded_file(stego_file, "stego")
                        
                        # Perform extraction
                        if method == "Traditional LSB":
                            extracted_message = extract_lsb_traditional(stego_path, message_length)
                        elif method == "Random Bit-Plane":
                            extracted_message = extract_random_bitplane(stego_path, message_length, secret_key)
                        else:  # Adaptive + Random
                            extracted_message = extract_adaptive_random(stego_path, message_length, secret_key)
                        
                        st.success("✅ Message extracted successfully!")
                        
                        # Display extracted message
                        st.markdown("---")
                        st.header("📨 Extracted Message")
                        st.markdown(f'<div class="success-box" style="font-size: 1.1em; font-family: monospace;">{extracted_message}</div>', unsafe_allow_html=True)
                        
                        st.info(f"📝 Extracted {len(extracted_message)} characters")
                        
                        # Cleanup
                        if os.path.exists(stego_path):
                            os.remove(stego_path)
                    
                    except Exception as e:
                        st.error(f"❌ Error during extraction: {str(e)}")
                        st.warning("💡 Tip: Make sure you're using the correct method and secret key!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>🔐 <strong>Advanced Image Steganography System</strong></p>
            <p style='font-size: 0.9em;'>Secure • Fast • Reliable</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
