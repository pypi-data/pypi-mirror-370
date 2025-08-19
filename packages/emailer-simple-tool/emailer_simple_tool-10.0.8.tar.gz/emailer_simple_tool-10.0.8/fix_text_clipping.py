#!/usr/bin/env python3
"""
Fix for text clipping issue in rotation - add proper padding for font metrics
"""

def fix_text_rotation_clipping():
    """
    The issue is that we're creating a temp image exactly the size of the text bounding box,
    but when we draw text at (0,0), parts of the text (especially descenders) can be clipped.
    
    Solution: Add padding to the temp image and adjust the text position accordingly.
    """
    
    # BEFORE (current code that clips):
    print("BEFORE - Current code that clips:")
    print("""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Problem: temp image is exactly the bbox size
    temp_img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # Problem: drawing at (0,0) can clip parts of the text
    temp_draw.text((0, 0), text, fill=color, font=font)
    """)
    
    # AFTER (fixed code with proper padding):
    print("\nAFTER - Fixed code with proper padding:")
    print("""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # FIX: Add padding for font metrics and descenders
    font_size = getattr(font, 'size', 50)
    padding = max(20, int(font_size * 0.3))  # 30% of font size, minimum 20px
    
    # FIX: Create temp image with padding
    temp_img = Image.new('RGBA', (text_width + 2*padding, text_height + 2*padding), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # FIX: Draw text with padding offset to avoid clipping
    temp_draw.text((padding, padding), text, fill=color, font=font)
    """)
    
    print("\nThis ensures:")
    print("✅ No clipping of descenders (g, j, p, q, y)")
    print("✅ No clipping of font ascenders") 
    print("✅ Proper space for font baseline offset")
    print("✅ Works with any font size")

if __name__ == "__main__":
    fix_text_rotation_clipping()
