import sys
import os
import warnings
import logging
import numpy as np
import re
from PIL import Image, ImageOps, ImageEnhance
import streamlit as st # Added Streamlit for caching

# Import PDF support
try:
    import fitz  
except ImportError:
    fitz = None

# Suppress warnings
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# === CONFIGURATION ===
LOCAL_MODEL_DIR = "trocr_model_large"
HF_MODEL_ID = "microsoft/trocr-large-handwritten"

@st.cache_resource # This keeps the model in memory so it doesn't reload on every click
def load_model():
    """
    Loads the TrOCR model. 
    Prioritizes local folder if it exists (faster), 
    otherwise downloads from HuggingFace (for GitHub/Cloud deployment).
    """
    path_to_use = HF_MODEL_ID # Default to online
    
    if os.path.exists(LOCAL_MODEL_DIR):
        print(f"📂 Found local model folder: '{LOCAL_MODEL_DIR}'")
        path_to_use = LOCAL_MODEL_DIR
    else:
        print(f"🌐 Local model not found. Downloading from HuggingFace: '{HF_MODEL_ID}'...")

    try:
        processor = TrOCRProcessor.from_pretrained(path_to_use)
        model = VisionEncoderDecoderModel.from_pretrained(path_to_use)
        print("✅ Model loaded successfully!")
        return processor, model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None, None

def clean_line_text(text):
    if "Categories" in text or "Living people" in text: return ""
    text = re.sub(r'^[\d\W_]{1,5}\s+', '', text)
    text = re.sub(r'\s+\d[\d\s]*$', '', text)
    text = text.replace(" .", ".")
    text = text.replace(" ,", ",")
    return text.strip()

def smart_polish_text(text):
    """
    Final Polish: Fixes merged words and specific OCR misreads.
    """
    # 1. Fix Math/Variable Confusion (kI -> k-1)
    text = re.sub(r'\bk\s*[-]?\s*[Il]\b', 'k-1', text)
    text = re.sub(r'\bkI\b', 'k-1', text)
    
    # 2. Fix Missing Hyphens
    text = re.sub(r'\bCrossvalidation\b', 'Cross-validation', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(\d+)fold\b', r'\1-fold', text)
    
    # 3. Fix Hallucinations
    text = text.replace("class signs", "classifiers")
    text = text.replace("guves", "gives")
    text = text.replace("refitable", "reliable")
    
    # 4. Fix Page Numbering
    text = re.sub(r'Page\s+I$', 'Page 1', text)

    # 5. Remove trailing artifact zeroes
    text = re.sub(r'\.0+$', '.', text)
    
    return text

def reconstruct_paragraph(text_lines):
    full_text = ""
    for line in text_lines:
        if not full_text:
            full_text = line
            continue
        if full_text.endswith("-"):
            full_text = full_text[:-1] + line
        else:
            full_text += " " + line

    full_text = re.sub(r'(\w+)\s*-\s*(\w+)', r'\1\2', full_text)
    full_text = smart_polish_text(full_text)
    return full_text

def remove_lines_and_find_text(image, page_num=0):
    gray = image.convert("L")
    w, h = gray.size
    crop_box = (0, 0, w, h)
    gray = gray.crop(crop_box)
    
    np_gray = np.array(gray)
    threshold = np.mean(np_gray) - 25 
    binary = (np_gray < threshold).astype(int)

    # === GRID ERASER ===
    b_h, b_w = binary.shape
    col_sums = np.sum(binary, axis=0)
    row_sums = np.sum(binary, axis=1)
    
    is_vert_line = col_sums > b_h * 0.50
    if np.any(is_vert_line): binary[:, is_vert_line] = 0
        
    is_horz_line = row_sums > b_w * 0.50
    if np.any(is_horz_line): binary[is_horz_line, :] = 0
    # ===================

    row_sums = np.sum(binary, axis=1)
    has_ink = row_sums > 5 
    
    lines = []
    start_y = None
    
    for y, is_ink in enumerate(has_ink):
        if is_ink and start_y is None:
            start_y = y
        elif not is_ink and start_y is not None:
            end_y = y
            height = end_y - start_y
            if height > 8: 
                pad = 4    
                lines.append((max(0, start_y - pad), min(h, end_y + pad)))
            start_y = None
            
    if start_y is not None:
        lines.append((start_y, len(has_ink)))
            
    return lines

def process_single_image(image, processor, model, page_num=1):
    print(f"✂️  Scanning Page {page_num}...")
    image = image.convert("RGB")
    line_coords = remove_lines_and_find_text(image, page_num)
    print(f"   - Found {len(line_coords)} lines.")
    
    page_lines = []
    for i, (y1, y2) in enumerate(line_coords):
        line_img = image.crop((0, y1, image.width, y2))
        
        if line_img.width < 1000:
            new_w = line_img.width * 2
            new_h = line_img.height * 2
            line_img = line_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        line_img = ImageOps.expand(line_img, border=10, fill='white')
        line_img = ImageOps.autocontrast(line_img.convert("L"), cutoff=1)
        line_img = line_img.convert("RGB")

        pixel_values = processor(images=line_img, return_tensors="pt").pixel_values
        generated_ids = model.generate(pixel_values, max_new_tokens=100)
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        cleaned = clean_line_text(text)
        if cleaned:
            page_lines.append(cleaned)
            print(".", end="", flush=True)
            
    print(" Done!")
    return reconstruct_paragraph(page_lines)

def main():
    print("\n" + "="*40)
    print("📑 UNIVERSAL RECOGNITION (SAVES TO 'ocr_output')")
    print("="*40)

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # If running in script mode, ask for input
        print("\nEnter path to Image or PDF file (drag & drop):")
        try:
            raw = input("> ").strip()
            if raw.startswith("& "): raw = raw[2:]
            file_path = raw.strip("'").strip('"').strip()
        except EOFError:
            return

    if not os.path.exists(file_path):
        print("❌ File not found.")
        return

    # === SETUP OUTPUT FOLDER ===
    output_folder = "ocr_output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 Created new folder: {output_folder}")

    # Generate Output Filename (uses the input filename)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_filename = f"{base_name}_ocr.txt"
    output_path = os.path.join(output_folder, output_filename)
    # ===========================

    processor, model = load_model()
    if processor is None:
        return

    full_document_text = []

    if file_path.lower().endswith(".pdf"):
        if fitz is None:
            print("\n❌ Error: PyMuPDF not installed. Run: pip install pymupdf")
            return
        print(f"\n📂 Processing PDF: {os.path.basename(file_path)}")
        doc = fitz.open(file_path)
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            content = process_single_image(img, processor, model, page_num=i+1)
            full_document_text.append(content)
    else:
        print(f"\n📂 Processing Image: {os.path.basename(file_path)}")
        img = Image.open(file_path)
        content = process_single_image(img, processor, model)
        full_document_text.append(content)

    final_output = "\n\n".join(full_document_text)

    # === SAVE TO FILE ===
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_output)
        print("\n" + "="*40)
        print(f"✅ SUCCESS! Output saved to:\n   {output_path}")
        print("="*40)
    except Exception as e:
        print(f"\n❌ Could not save file: {e}")

    # Print to console as well
    print("\n📜 PREVIEW:")
    print("-" * 20)
    print(final_output)
    print("-" * 20 + "\n")

if __name__ == "__main__":
    main()