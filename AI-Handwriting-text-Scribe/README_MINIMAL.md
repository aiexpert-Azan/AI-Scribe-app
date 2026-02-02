# 🖋️ AI Scribe: Intelligent Handwriting Synthesis & OCR

**AI Scribe** is a dual-module AI application that bridges the gap between digital text and analog handwriting. It features a **Generative Writer** that converts typed text into realistic, vector-based handwriting (simulating human motor control) and an **Optical Character Recognition (OCR)** engine capable of reading complex, unconstrained handwritten documents.

## 🚀 Features

### 1. The Writer (Synthesis)
* **Vector-Based Generation:** Uses RNNs (LSTMs) + Mixture Density Networks (MDN) to generate "strokes" rather than pixels.
* **Multi-Style Support:** Choose from **13 distinct handwriting styles** (cursive, print, messy, neat).
* **AI Assistant:** Integrated Chatbot (powered by Google Gemini) to help draft content.
* **Export:** Saves outputs as high-quality SVGs or PDFs.

### 2. The Reader (OCR)
* **Transformer Architecture:** Powered by Microsoft's **TrOCR (Transformer OCR)**.
* **Intelligent Segmentation:** Custom algorithms to detect lines and remove ruled paper grids.
* **Format Support:** Drag-and-drop support for Images (PNG, JPG) and PDFs.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/handwriting_synthesis.git](https://github.com/YOUR_USERNAME/handwriting_synthesis.git)
    cd handwriting_synthesis
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🧠 Model Setup (OCR Engine)

This project uses the **Microsoft TrOCR Large** model (~1.5 GB). Due to GitHub's file size limits, the model is not included in the repository. You can set it up in two ways:

### Option A: Automatic Download (Easiest)
Simply run the application. The first time you use the "Reader (OCR)" page, the app will automatically download the necessary files from Hugging Face.

### Option B: Manual Download (Faster)
If you prefer to pre-download the model (recommended for slow internet):

1.  **Create a folder** inside your project directory named exactly:
    ```text
    trocr_model_large
    ```

2.  **Download the files** from the [Hugging Face Repository](https://huggingface.co/microsoft/trocr-large-handwritten/tree/main).

3.  **Save these 8 specific files** into the `trocr_model_large` folder:
    * `pytorch_model.bin` (Main model weights - 1.23 GB)
    * `config.json`
    * `preprocessor_config.json`
    * `tokenizer.json`
    * `tokenizer_config.json`
    * `special_tokens_map.json`
    * `vocab.json`
    * `merges.txt`

---

## 🏃 Usage

Run the main application:
```bash
streamlit run app.py