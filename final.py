import tkinter as tk #gui
from tkinter import filedialog, messagebox, scrolledtext, ttk
import pdfplumber #extract pdf
from docx import Document
import os #file path
import re #text processing
import pyttsx3  #text to speech.

# NLP libraries
import spacy #NER
from rake_nltk import Rake 
from textblob import TextBlob #sentiment analysis
import yake #Extracts keywords from text
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class PDFNLPToolkit:
    def __init__(self, root):
        self.root = root
        self.root.title("📄 PDF NLP Toolkit")
        self.root.geometry("900x700")
        self.root.configure(bg="#F0F0F0")

        self.file_path_var = tk.StringVar()
        tk.Label(root, textvariable=self.file_path_var, bg="#F0F0F0", font=("Arial", 10)).pack(pady=5)

        # Buttons
        self.create_buttons()

        # Text Area
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30, font=("Courier", 10))
        self.text_area.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # NLP models
        self.nlp = spacy.load("en_core_web_sm")

        self.pdf_path = ""
        self.extracted_text = ""

    def create_buttons(self):
        """Create buttons with improved GUI and dropdowns."""
        button_frame = tk.Frame(self.root, bg="#F0F0F0")
        button_frame.pack(pady=10)

        buttons = [
            ("👤 Select PDF", self.load_pdf, "#FFD700"),
            ("📝 Extract Text", self.extract_text, "#32CD32"),
            ("🔍 Summarize", self.summarize_text, "#1E90FF"),
            ("💾 Save Text", self.save_text, "#4CAF50"),
            ("🧠 NER", self.extract_entities, "#FF6347"),
            ("🔑 Keywords", self.extract_keywords, "#FFA500"),
            ("😊 Sentiment", self.analyze_sentiment, "#9370DB"),
            ("📛 Speak", self.text_to_speech, "#8A2BE2"),
            ("❌ Clear", self.clear_text, "#FF4500")
        ]

        for text, command, color in buttons:
            tk.Button(button_frame, text=text, command=command, bg=color, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

    def load_pdf(self):
        """Load a PDF file."""
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_path = file_path
            self.file_path_var.set(f"Selected: {os.path.basename(file_path)}")

    def extract_text(self):
        """Extract text from the PDF."""
        if not self.pdf_path:
            messagebox.showwarning("Warning", "Select a PDF first!")
            return

        try:
            self.text_area.delete(1.0, tk.END)
            with pdfplumber.open(self.pdf_path) as pdf:
                self.extracted_text = "\n\n".join(page.extract_text() or "" for page in pdf.pages)

            self.extracted_text = re.sub(r'\s+', ' ', self.extracted_text).strip()
            self.text_area.insert(tk.END, self.extracted_text)
            messagebox.showinfo("Success", "Text extracted!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    def save_text(self):
        """Save extracted text to a file."""
        if not self.extracted_text:
            messagebox.showwarning("Warning", "No text to save!")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("Word Files", "*.docx")])
        if file_path:
            if file_path.endswith(".docx"):
                doc = Document()
                doc.add_paragraph(self.extracted_text)
                doc.save(file_path)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.extracted_text)
            messagebox.showinfo("Success", "File saved!")

    def summarize_text(self):
        """Summarize extracted text using spaCy sentence segmentation."""
        if not self.extracted_text:
            messagebox.showwarning("Warning", "Extract text first!")
            return

        doc = self.nlp(self.extracted_text)
        sentences = [sent.text for sent in doc.sents]
        summary_text = " ".join(sentences[:5])  # Show the first 5 sentences

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "--- SUMMARY ---\n" + summary_text)

    def extract_entities(self):
        """Perform Named Entity Recognition (NER) with improved filtering."""
        if not self.extracted_text:
            messagebox.showwarning("Warning", "Extract text first!")
            return

        doc = self.nlp(self.extracted_text)
        entity_labels = {"ORG", "PERSON", "DATE", "PERCENT", "CARDINAL", "PRODUCT"}  # Relevant entity types
        entities = [f"{ent.text} ({ent.label_})" for ent in doc.ents if ent.label_ in entity_labels and len(ent.text) > 1]
        
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "--- NAMED ENTITIES ---\n" + "\n".join(entities))

    def extract_keywords(self):
        """Extract keywords using YAKE."""
        if not self.extracted_text:
            messagebox.showwarning("Warning", "Extract text first!")
            return

        extractor = yake.KeywordExtractor()
        keywords = extractor.extract_keywords(self.extracted_text)
        keyword_text = "\n".join(f"{word} ({score:.2f})" for word, score in keywords[:10])
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "--- KEYWORDS ---\n" + keyword_text)

    def analyze_sentiment(self):
        """Perform sentiment analysis using VADER."""
        if not self.extracted_text:
            messagebox.showwarning("Warning", "Extract text first!")
            return

        analyzer = SentimentIntensityAnalyzer()
        sentiment = analyzer.polarity_scores(self.extracted_text)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, f"Sentiment: {sentiment}")

    def text_to_speech(self):
        """Convert extracted text to speech."""
        if self.extracted_text:
            engine = pyttsx3.init()
            engine.say(self.extracted_text[:500])
            engine.runAndWait()

    def clear_text(self):
        self.text_area.delete(1.0, tk.END)

root = tk.Tk()
PDFNLPToolkit(root)
root.mainloop()