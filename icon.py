#!/usr/bin/env python3
"""
Generate a simple icon for Media Archive Manager.

This script creates a simple ICO file with a media/archive theme.
The icon is a simple design with a folder and media symbol.
"""

import struct
from pathlib import Path


def create_simple_icon():
    """Create a simple 32x32 icon with a media/archive theme."""
    
    # Create a simple 32x32 BMP image (blue folder with white background)
    # This is a minimal valid BMP that we'll convert to ICO
    
    # BMP Header (14 bytes)
    bmp_header = bytearray()
    bmp_header.extend(b'BM')  # Signature
    bmp_header.extend(struct.pack('<I', 1078))  # File size (14 + 40 + 1024 + 32*32)
    bmp_header.extend(struct.pack('<I', 0))  # Reserved
    bmp_header.extend(struct.pack('<I', 1078))  # Offset to pixel data
    
    # DIB Header (40 bytes)
    dib_header = bytearray()
    dib_header.extend(struct.pack('<I', 40))  # Header size
    dib_header.extend(struct.pack('<i', 32))  # Width
    dib_header.extend(struct.pack('<i', 64))  # Height (doubled for AND mask)
    dib_header.extend(struct.pack('<H', 1))  # Planes
    dib_header.extend(struct.pack('<H', 8))  # Bits per pixel
    dib_header.extend(struct.pack('<I', 0))  # Compression
    dib_header.extend(struct.pack('<I', 0))  # Image size
    dib_header.extend(struct.pack('<i', 0))  # X pixels per meter
    dib_header.extend(struct.pack('<i', 0))  # Y pixels per meter
    dib_header.extend(struct.pack('<I', 256))  # Colors used
    dib_header.extend(struct.pack('<I', 0))  # Important colors
    
    # Color palette (256 colors, 4 bytes each)
    palette = bytearray()
    # White background
    palette.extend(b'\xFF\xFF\xFF\x00')  # Color 0: White
    # Blue for folder
    palette.extend(b'\x00\x00\xFF\x00')  # Color 1: Blue
    # Gray for shadow
    palette.extend(b'\x80\x80\x80\x00')  # Color 2: Gray
    # Fill rest with black
    for i in range(3, 256):
        palette.extend(b'\x00\x00\x00\x00')
    
    # Pixel data (32x32 = 1024 bytes, stored bottom-up)
    pixels = bytearray(1024)
    
    # Create a simple folder icon pattern
    # Fill with white (0)
    for i in range(1024):
        pixels[i] = 0
    
    # Draw folder shape (simplified)
    # Top part (folder tab)
    for y in range(8, 12):
        for x in range(4, 12):
            pixels[y * 32 + x] = 1  # Blue
    
    # Main folder body
    for y in range(12, 28):
        for x in range(2, 30):
            pixels[y * 32 + x] = 1  # Blue
    
    # Add some detail (darker blue border)
    for y in range(12, 28):
        pixels[y * 32 + 2] = 2  # Gray border
        pixels[y * 32 + 29] = 2  # Gray border
    
    # AND mask (transparency mask) - all zeros means opaque
    and_mask = bytearray(1024)
    
    # Combine BMP
    bmp_data = bmp_header + dib_header + palette + pixels + and_mask
    
    # Create ICO file
    ico_data = bytearray()
    
    # ICO Header (6 bytes)
    ico_data.extend(struct.pack('<H', 0))  # Reserved
    ico_data.extend(struct.pack('<H', 1))  # Type (1 = ICO)
    ico_data.extend(struct.pack('<H', 1))  # Number of images
    
    # Image Directory Entry (16 bytes)
    ico_data.extend(struct.pack('<B', 32))  # Width
    ico_data.extend(struct.pack('<B', 32))  # Height
    ico_data.extend(struct.pack('<B', 0))  # Color count (0 = no palette)
    ico_data.extend(struct.pack('<B', 0))  # Reserved
    ico_data.extend(struct.pack('<H', 1))  # Color planes
    ico_data.extend(struct.pack('<H', 8))  # Bits per pixel
    ico_data.extend(struct.pack('<I', len(bmp_data)))  # Size of image data
    ico_data.extend(struct.pack('<I', 22))  # Offset to image data
    
    # Add BMP data
    ico_data.extend(bmp_data)
    
    return bytes(ico_data)


def create_icon_file():
    """Create the icon.ico file."""
    try:
        icon_data = create_simple_icon()
        icon_path = Path(__file__).parent / "icon.ico"
        
        with open(icon_path, 'wb') as f:
            f.write(icon_data)
        
        print(f"[OK] Icon created: {icon_path}")
        print(f"     Size: {len(icon_data)} bytes")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating icon: {e}")
        return False


if __name__ == "__main__":
    create_icon_file()
