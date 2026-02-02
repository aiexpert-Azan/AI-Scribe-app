# 🖋️ AI Scribe: Intelligent Handwriting Synthesis & OCR

**AI Scribe** is a dual-module AI application that bridges the gap between digital text and analog handwriting. It features a **Generative Writer** that converts typed text into realistic, vector-based handwriting (simulating human motor control) and an **Optical Character Recognition (OCR)** engine capable of reading complex, unconstrained handwritten documents.

<div align="center">
  <h3>👇 Click below to watch the full demo video 👇</h3>
  <a href="https://www.youtube.com/watch?v=hc8wq16-BYs">
    <img src="https://img.youtube.com/vi/hc8wq16-BYs/0.jpg" alt="Watch the Demo">
  </a>
</div>

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
    git clone https://github.com/Who-Moiz/AI-Handwriting-text-Scribe.git
    cd AI-Handwriting-text-Scribe
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

 ```
Writer Tab: Type text, pick a style, and click "Generate".  
Reader Tab: Upload an image or PDF to extract text.  
Assistant Tab: Chat with AI to generate content.

---

## 📂 Project Structure

AI-Handwriting-Scribe/  
│  
├── app.py                 # Main entry point & Writer Interface  
├── ocr_page.py            # OCR (Reader) Module Logic  
├── drawing.py             # Vector stroke rendering logic  
├── hand.py                # RNN Model Architecture  
├── requirements.txt       # Project Dependencies  
├── README.md              # Documentation  
│  
├── checkpoints/           # Pre-trained Synthesis Model Weights  
│   ├── model.meta  
│   └── ...  
│  
├── styles/                # Pre-defined Handwriting Styles (.npy)  
│   ├── style-0-strokes.npy  
│   └── ...  
│  
└── trocr_model_large/     # (Local Only) OCR Model Weights  
    └── pytorch_model.bin  

---
    
## 🧠 Tech Stack

**Frontend:** Streamlit  
**Synthesis:** TensorFlow (RNN/LSTM/MDN)  
**OCR:** PyTorch, Transformers (Hugging Face)  
**Processing:** OpenCV, Pillow, SVGWrite, PyMuPDF  
**AI Assistant:** Google Gemini API

---

## 📜 Credits

**Synthesis Model:** Based on the research by Alex Graves (Generating Sequences With Recurrent Neural Networks).

**OCR Model**: Microsoft TrOCR (Transformer-based Optical Character Recognition).

**Dataset:** IAM On-Line Handwriting Database.
