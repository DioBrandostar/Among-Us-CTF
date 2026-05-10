"""
EXIF Metadata Embedding Script for Security Room
=================================================
Run this script AFTER placing your surveillance photo.

It embeds a Caesar cipher (ROT13) encoded flag into the EXIF metadata
of the surveillance photo for the Security Room challenge.

Usage:
    python embed_exif.py

Requirements:
    pip install Pillow piexif

Input:  app/static/images/surveillance_corrupted.jpg
Output: Overwrites the same file with EXIF metadata embedded
"""

import os
import sys

try:
    import piexif
    from PIL import Image
except ImportError:
    print("ERROR: Required libraries not found.")
    print("Run: pip install Pillow piexif")
    sys.exit(1)


def caesar_cipher(text, shift):
    """Apply Caesar cipher with given shift."""
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base + shift) % 26 + base))
        else:
            result.append(char)
    return ''.join(result)


def embed_exif_metadata(image_path, hidden_text):
    """Embed hidden text into the EXIF UserComment and ImageDescription fields."""
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found at {image_path}")
        print("Please place your surveillance photo there first!")
        return False

    # Open image
    img = Image.open(image_path)

    # Build EXIF data
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

    # Store the Caesar cipher text in ImageDescription
    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = hidden_text.encode('utf-8')

    # Also store in UserComment for redundancy
    user_comment = b"ASCII\x00\x00\x00" + hidden_text.encode('utf-8')
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comment

    # Add some realistic-looking metadata
    exif_dict["0th"][piexif.ImageIFD.Make] = b"HORIZON-7 CCTV SYSTEM"
    exif_dict["0th"][piexif.ImageIFD.Model] = b"CAM-04 Security Module"
    exif_dict["0th"][piexif.ImageIFD.Software] = b"Orion-9 Surveillance v3.2.1"
    exif_dict["0th"][piexif.ImageIFD.Artist] = b"SYSTEM AUTO-CAPTURE"
    exif_dict["0th"][piexif.ImageIFD.Copyright] = b"Interstellar Recovery Authority"

    # Generate EXIF bytes
    exif_bytes = piexif.dump(exif_dict)

    # Save with EXIF
    img.save(image_path, "JPEG", exif=exif_bytes, quality=95)
    print(f"✅ EXIF metadata embedded successfully into: {image_path}")
    print(f"   Hidden text (Caesar cipher): {hidden_text}")
    return True


if __name__ == '__main__':
    # The original flag
    original_flag = "FLAG{surveil_cam_breach}"

    # Caesar cipher with shift 13 (ROT13)
    encoded_flag = caesar_cipher(original_flag, 13)
    print(f"Original flag:  {original_flag}")
    print(f"Encoded (ROT13): {encoded_flag}")
    print()

    # Path to the surveillance photo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, 'app', 'static', 'images', 'surveillance_corrupted.jpg')

    embed_exif_metadata(image_path, encoded_flag)

    print()
    print("=" * 50)
    print("VERIFICATION — Reading back EXIF data:")
    print("=" * 50)

    try:
        exif_data = piexif.load(image_path)
        desc = exif_data["0th"].get(piexif.ImageIFD.ImageDescription, b"").decode('utf-8')
        print(f"ImageDescription: {desc}")

        comment = exif_data["Exif"].get(piexif.ExifIFD.UserComment, b"")
        if comment.startswith(b"ASCII\x00\x00\x00"):
            comment = comment[8:].decode('utf-8')
        print(f"UserComment: {comment}")

        make = exif_data["0th"].get(piexif.ImageIFD.Make, b"").decode('utf-8')
        model = exif_data["0th"].get(piexif.ImageIFD.Model, b"").decode('utf-8')
        print(f"Camera: {make} — {model}")
    except Exception as e:
        print(f"Verification error: {e}")
