import os
import sys
import time
from openai import OpenAI

# 1. SETUP TENSORFLOW ENVIRONMENT
os.environ['TF_USE_LEGACY_KERAS'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 2. IMPORT HANDWRITING MODULES
try:
    from demo import Hand
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPDF
        from reportlab.pdfgen import canvas
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False
        print("⚠️  PDF libraries missing. Install with: pip install svglib reportlab")
    
    HANDWRITING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Handwriting modules not found: {e}")
    print("    (Running in TEXT-ONLY mode)")
    HANDWRITING_AVAILABLE = False

# ==========================================
# 3. HELPER FUNCTION: MERGE TO PDF
# ==========================================
def save_response_as_pdf(svg_files, output_filename):
    if not PDF_AVAILABLE or not svg_files:
        return
    
    try:
        c = canvas.Canvas(output_filename, pagesize=(1860, 3508)) 
        for svg_file in svg_files:
            drawing = svg2rlg(svg_file)
            renderPDF.draw(drawing, c, 0, 0)
            c.showPage()
            try: os.remove(svg_file) 
            except: pass
            
        c.save()
        print(f"📄 Saved as PDF: {os.path.abspath(output_filename)}")
    except Exception as e:
        print(f"❌ Error saving PDF: {e}")

# ==========================================
# 4. MAIN APPLICATION
# ==========================================
class HandwritingBot:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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"
        )
        
        self.hand_model = None
        if HANDWRITING_AVAILABLE:
            print("\n⏳ Loading Handwriting Model...")
            self.hand_model = Hand()
            print("✅ Model Loaded!")

    def generate_handwriting(self, text, style_id):
        if not self.hand_model:
            return

        print(f"\n✍️  Synthesizing handwriting (Style {style_id})...")
        
        timestamp = int(time.time())
        filename_base = f"output_style{style_id}_{timestamp}.svg"
        pdf_filename = f"output_style{style_id}_{timestamp}.pdf"

        # Pass the selected style_id to the writer
        generated_svgs = self.hand_model.write(
            filename=filename_base,
            lines=text,
            biases=[0.75],       # Standard neatness
            styles=[style_id],   # USER SELECTED STYLE
            page_width=1860,
            page_height=3508,
            ruled=True
        )

        save_response_as_pdf(generated_svgs, pdf_filename)

    def get_user_style(self):
        """Asks the user for a style number 0-12"""
        while True:
            try:
                val = input("\n🎨 Choose Handwriting Style (0-12) [Default 0]: ").strip()
                if val == "": return 0
                style = int(val)
                if 0 <= style <= 12:
                    return style
                print("❌ Please enter a number between 0 and 12.")
            except ValueError:
                print("❌ Invalid number.")

    def start(self):
        print("\n" + "="*50)
        print("🤖 AI SCRIBE (Single Execution Mode)")
        print("="*50)

        # 1. Ask for Style FIRST
        selected_style = self.get_user_style()

        # 2. Ask for the Prompt
        user_input = input("\n📝 What should I write about? (e.g. 'Explain Atoms'): ").strip()
        if not user_input:
            print("No input provided. Exiting.")
            return

        # System Prompt
        system_instruction = (
            "You are a helpful AI assistant whose output will be converted into HANDWRITING. "
            "Formatting Rules:\n"
            "1. NO Markdown (**bold**, *italics*).\n"
            "2. NO Emojis.\n"
            "3. NO Code Blocks.\n"
            "4. Keep answers plain, clear, and concise."
        )

        try:
            print("Thinking...", end="\r")
            
            # 3. Get AI Response
            response = self.client.chat.completions.create(
                model="google/gemini-2.0-flash-001", 
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_input}
                ]
            )
            bot_text = response.choices[0].message.content.strip()
            
            print(f"\n🤖 Bot Response:\n{'-'*20}\n{bot_text}\n{'-'*20}")

            # 4. Generate Handwriting
            self.generate_handwriting(bot_text, selected_style)
            
            print("\n✅ Job Done. Exiting...")

        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    app = HandwritingBot()
    app.start()