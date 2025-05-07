import pytesseract
from PIL import Image
import difflib
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(image_path):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

def get_diff_highlight(pdf_text, email_text):
    pdf_words = pdf_text.split()
    email_words = email_text.split()

    diff = list(difflib.ndiff(pdf_words, email_words))

    highlighted_pdf = []
    highlighted_email = []

    for word in diff:
        if word.startswith('  '):  # Common words
            highlighted_pdf.append(word[2:])
            highlighted_email.append(word[2:])
        elif word.startswith('- '):  # Missing from email
            highlighted_pdf.append(('MISSING', word[2:]))
        elif word.startswith('+ '):  # Extra in email
            highlighted_email.append(('EXTRA', word[2:]))

    return highlighted_pdf, highlighted_email

def upload_pdf_image():
    filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if filepath:
        pdf_path_var.set(filepath)

def upload_email_image():
    filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if filepath:
        email_path_var.set(filepath)

def run_comparison():
    pdf_path = pdf_path_var.get()
    email_path = email_path_var.get()

    if not pdf_path or not email_path:
        messagebox.showerror("Error", "Please select both images.")
        return

    try:
        pdf_text = extract_text(pdf_path)
        email_text = extract_text(email_path)
        pdf_result, email_result = get_diff_highlight(pdf_text, email_text)

        result_window = tk.Toplevel(root)
        result_window.title("Comparison Result")
        result_window.geometry("1000x500")
        result_window.grid_columnconfigure(0, weight=1)
        result_window.grid_columnconfigure(1, weight=1)

        # PDF viewer
        tk.Label(result_window, text="PDF Text (Source)", font=("Arial", 12, "bold")).grid(row=0, column=0)
        pdf_box = ScrolledText(result_window, wrap=tk.WORD, font=("Arial", 10))
        pdf_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        for word in pdf_result:
            if isinstance(word, tuple) and word[0] == 'MISSING':
                pdf_box.insert(tk.END, word[1] + ' ', 'missing')
            else:
                pdf_box.insert(tk.END, word + ' ')
        pdf_box.tag_config('missing', foreground='orange')
        pdf_box.config(state='disabled')

        # Email viewer
        tk.Label(result_window, text="Live Email Text", font=("Arial", 12, "bold")).grid(row=0, column=1)
        email_box = ScrolledText(result_window, wrap=tk.WORD, font=("Arial", 10))
        email_box.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        for word in email_result:
            if isinstance(word, tuple) and word[0] == 'EXTRA':
                email_box.insert(tk.END, word[1] + ' ', 'extra')
            else:
                email_box.insert(tk.END, word + ' ')
        email_box.tag_config('extra', foreground='red')
        email_box.config(state='disabled')

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Main UI
root = tk.Tk()
root.title("Image Text Comparison Tool")
root.geometry("600x250")

pdf_path_var = tk.StringVar()
email_path_var = tk.StringVar()

tk.Label(root, text="PDF Image", font=("Arial", 10)).pack(pady=(10, 0))
tk.Entry(root, textvariable=pdf_path_var, width=60).pack()
tk.Button(root, text="Upload PDF Image", command=upload_pdf_image).pack(pady=5)

tk.Label(root, text="Live Email Image", font=("Arial", 10)).pack(pady=(10, 0))
tk.Entry(root, textvariable=email_path_var, width=60).pack()
tk.Button(root, text="Upload Live Email Image", command=upload_email_image).pack(pady=5)

tk.Button(root, text="Compare Text", command=run_comparison, bg="lightblue", font=("Arial", 10, "bold")).pack(pady=15)

root.mainloop()
