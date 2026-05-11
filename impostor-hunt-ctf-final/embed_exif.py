"""
EXIF Metadata Embedding Script for Security Room
=================================================
Run this script AFTER placing your surveillance photo.

It embeds a Vigenère cipher encoded flag into the EXIF metadata
of the surveillance photo for the Security Room challenge.

The keyword "HORIZON" is hidden naturally in the Software field
as part of the camera system name.

Usage:
    python embed_exif.py

Requirements:
    pip install Pillow piexif

Input:  app/static/images/surveillance_corrupted.jpg (or .png auto-converted)
Output: Overwrites as JPEG with EXIF metadata embedded
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


def vigenere_encrypt(plaintext, keyword):
    """Encrypt text using Vigenère cipher. Only encrypts alpha chars."""
    result = []
    key_idx = 0
    keyword = keyword.upper()
    for char in plaintext:
        if char.isalpha():
            shift = ord(keyword[key_idx % len(keyword)]) - ord('A')
            if char.isupper():
                result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
            else:
                result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
            key_idx += 1
        else:
            result.append(char)
    return ''.join(result)


def embed_exif_metadata(image_path, hidden_text):
    """Embed hidden text into the EXIF UserComment and ImageDescription fields."""
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found at {image_path}")
        print("Please place your surveillance photo there first!")
        return False

    # Open image and convert to RGB (needed for JPEG)
    img = Image.open(image_path).convert('RGB')

    # Build EXIF data
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

    # Store the Vigenère cipher text in ImageDescription
    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = hidden_text.encode('utf-8')

    # Also store in UserComment for redundancy
    user_comment = b"ASCII\x00\x00\x00" + hidden_text.encode('utf-8')
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comment

    # Add realistic-looking metadata — keyword is hidden naturally here
    exif_dict["0th"][piexif.ImageIFD.Make] = b"SecureStar Industries"
    exif_dict["0th"][piexif.ImageIFD.Model] = b"CAM-04 Night Vision Module"
    # The word "Horizon" appears naturally as part of the software name
    # This is the Vigenère keyword the player needs to find
    exif_dict["0th"][piexif.ImageIFD.Software] = b"Horizon Integrated Monitoring Suite v3.2"
    exif_dict["0th"][piexif.ImageIFD.Artist] = b"SYSTEM AUTO-CAPTURE"
    exif_dict["0th"][piexif.ImageIFD.Copyright] = b"Interstellar Recovery Authority - 2147"

    # Generate EXIF bytes
    exif_bytes = piexif.dump(exif_dict)

    # Save as JPEG with EXIF
    output_path = image_path.replace('.png', '.jpg') if image_path.endswith('.png') else image_path
    img.save(output_path, "JPEG", exif=exif_bytes, quality=95)
    print(f"✅ EXIF metadata embedded successfully into: {output_path}")
    print(f"   Hidden text (Vigenère cipher): {hidden_text}")
    return True


if __name__ == '__main__':
    # The original flag
    original_flag = "FLAG{surveil_cam_breach}"
    keyword = "HORIZON"

    # Vigenère encrypt
    encoded_flag = vigenere_encrypt(original_flag, keyword)
    print(f"Original flag:       {original_flag}")
    print(f"Keyword:             {keyword}")
    print(f"Encoded (Vigenère):  {encoded_flag}")
    print()

    # Path to the surveillance photo — check for both PNG and JPG
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'app', 'static', 'images')

    # Try to find the uploaded image
    source_image = None
    for fname in os.listdir(images_dir):
        if fname.endswith(('.png', '.jpg', '.jpeg')):
            source_image = os.path.join(images_dir, fname)
            break

    if not source_image:
        print("ERROR: No image found in app/static/images/")
        sys.exit(1)

    print(f"Source image: {source_image}")

    # Convert and save as surveillance_corrupted.jpg
    output_path = os.path.join(images_dir, 'surveillance_corrupted.jpg')

    img = Image.open(source_image).convert('RGB')
    img.save(output_path, "JPEG", quality=95)
    print(f"Converted to JPEG: {output_path}")

    # Now embed EXIF
    embed_exif_metadata(output_path, encoded_flag)

    print()
    print("=" * 50)
    print("VERIFICATION — Reading back EXIF data:")
    print("=" * 50)

    try:
        exif_data = piexif.load(output_path)
        desc = exif_data["0th"].get(piexif.ImageIFD.ImageDescription, b"").decode('utf-8')
        print(f"ImageDescription: {desc}")

        comment = exif_data["Exif"].get(piexif.ExifIFD.UserComment, b"")
        if comment.startswith(b"ASCII\x00\x00\x00"):
            comment = comment[8:].decode('utf-8')
        print(f"UserComment: {comment}")

        make = exif_data["0th"].get(piexif.ImageIFD.Make, b"").decode('utf-8')
        model = exif_data["0th"].get(piexif.ImageIFD.Model, b"").decode('utf-8')
        software = exif_data["0th"].get(piexif.ImageIFD.Software, b"").decode('utf-8')
        print(f"Camera: {make} — {model}")
        print(f"Software: {software}")
        print()
        print(f"🔑 The Vigenère keyword '{keyword}' is hidden in the Software field")
        print(f"   Player must decode: {encoded_flag} → {original_flag}")
    except Exception as e:
        print(f"Verification error: {e}")
