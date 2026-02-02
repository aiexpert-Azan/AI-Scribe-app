import argparse
import os
from demo import Hand

# ================= PAGE SETTINGS =================
PAGE_WIDTH = 1860  
PAGE_HEIGHT = 3508

LEFT_MARGIN = 150
RIGHT_MARGIN = 150
TOP_MARGIN = 250
BOTTOM_MARGIN = 250
# =================================================

def merge_to_pdf(svg_files, final_pdf_name):
    if not svg_files: return
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPDF
        from reportlab.pdfgen import canvas
        
        print("\n📚 Merging into PDF...")
        c = canvas.Canvas(final_pdf_name, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
        for svg_file in svg_files:
            print(f"   Processing {svg_file}...")
            drawing = svg2rlg(svg_file)
            renderPDF.draw(drawing, c, 0, 0)
            c.showPage()
        c.save()
        print(f"✅ FINAL PDF SAVED: {os.path.abspath(final_pdf_name)}")
    except ImportError:
        print("\n⚠️ PDF Error: Install libraries with 'pip install svglib reportlab'")

def main():
    parser = argparse.ArgumentParser(description="Generate notebook-style handwritten text.")
    parser.add_argument("--text", type=str, help="Text to synthesize")
    parser.add_argument("--style", type=int, help="Handwriting style (0-12)")
    parser.add_argument("--bias", type=float, help="Bias (0.5–1.0)")
    parser.add_argument("--output", type=str, default="notebook.svg", help="Output filename")

    args = parser.parse_args()

    # 1. Get Text
    text = args.text
    if not text:
        print("\nPaste your text below:")
        text = input("> ").strip()
    if not text: return
    text = text.replace("\\n", "\n")

    # 2. Get Style (Interactive)
    style = args.style
    if style is None:
        while True:
            try:
                val = input("\nChoose Handwriting Style (0-12) [Default 0]: ").strip()
                if val == "": 
                    style = 0
                    break
                style = int(val)
                if 0 <= style <= 12: break
                print("❌ Please enter a number between 0 and 12.")
            except ValueError:
                print("❌ Invalid number.")

    # 3. Get Bias (Interactive)
    bias = args.bias
    if bias is None:
        while True:
            try:
                val = input("Choose Bias (0.5=messy, 1.0=neat) [Default 0.75]: ").strip()
                if val == "": 
                    bias = 0.75
                    break
                bias = float(val)
                break
            except ValueError:
                print("❌ Invalid number.")

    print("\n" + "=" * 60)
    print("📝 Generating Multi-Page Handwriting")
    print(f"Style: {style} | Bias: {bias}")
    print("=" * 60)

    hand = Hand()

    generated_svgs = hand.write(
        filename=args.output,
        lines=text, 
        biases=[bias],
        styles=[style],
        page_width=PAGE_WIDTH,
        page_height=PAGE_HEIGHT,
        margins={
            "left": LEFT_MARGIN,
            "right": RIGHT_MARGIN,
            "top": TOP_MARGIN,
            "bottom": BOTTOM_MARGIN
        },
        ruled=True
    )

    pdf_name = args.output.replace(".svg", ".pdf")
    merge_to_pdf(generated_svgs, pdf_name)

if __name__ == "__main__":
    main()