import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import PyPDF2
import requests
import threading
import json

def call_reverse_api(msg):
    url = "ENTER YOUR REVERSE API URL"
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"msg": msg})

    try:
        resp = requests.post(url, headers=headers, data=data)
        resp.raise_for_status()
        return resp.json().get('response', 'No response')  # Adjust based on your API's response format
    except requests.exceptions.RequestException as e:
        messagebox.showerror("API Error", f"An error occurred: {str(e)}")
        return ""

def extract_text_from_pdf(pdf_path, progress_var):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            for page_num in range(total_pages):
                try:
                    page = reader.pages[page_num]
                    text += page.extract_text() or ""
                except Exception:
                    continue
                progress_var.set((page_num + 1) / total_pages * 100)
    except Exception as e:
        messagebox.showerror("File Error", f"Failed to process PDF: {e}")
    return text

def summarize_text(text):
    prompt = f"Summarize the following text:\n{text}"
    summary = call_reverse_api(prompt)
    return summary

def ask_question_about_text(text, question):
    prompt = f"Text: {text}\nQuestion: {question}\nAnswer:"
    answer = call_reverse_api(prompt)
    return answer

def upload_pdf(progress_var):
    global pdf_text
    filepath = filedialog.askopenfilename(
        title="Select a PDF File",
        filetypes=(("PDF Files", "*.pdf"),)
    )
    if filepath:
        status_label.config(text="Processing PDF...")
        pdf_text = extract_text_from_pdf(filepath, progress_var)
        status_label.config(text="PDF processed successfully!")
        messagebox.showinfo("Success", "PDF uploaded and text extracted!")
    else:
        messagebox.showerror("Error", "No PDF selected!")

def upload_pdf_threaded():
    progress_var.set(0)
    upload_button.config(state=tk.DISABLED)
    threading.Thread(target=upload_pdf, args=(progress_var,)).start()
    upload_button.config(state=tk.NORMAL)

def summarize_pdf():
    if pdf_text:
        summary = summarize_text(pdf_text)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, summary)
    else:
        messagebox.showerror("Error", "Please upload a PDF first!")

def ask_question():
    if pdf_text:
        question = question_entry.get()
        if question:
            answer = ask_question_about_text(pdf_text, question)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, answer)
        else:
            messagebox.showerror("Error", "Please enter a question!")
    else:
        messagebox.showerror("Error", "Please upload a PDF first!")

root = tk.Tk()
root.title("PDF Analyzer")

upload_button = tk.Button(root, text="Upload PDF", padx=10, pady=5, command=upload_pdf_threaded)
upload_button.pack()

summarize_button = tk.Button(root, text="Summarize PDF", padx=10, pady=5, command=summarize_pdf)
summarize_button.pack()

question_label = tk.Label(root, text="Ask a question about the PDF:")
question_label.pack()

question_entry = tk.Entry(root, width=50)
question_entry.pack()

ask_button = tk.Button(root, text="Ask Question", padx=10, pady=5, command=ask_question)
ask_button.pack()

result_text = tk.Text(root, height=20, width=80)
result_text.pack()

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, padx=20, pady=10)

status_label = tk.Label(root, text="")
status_label.pack()

pdf_text = ""

root.mainloop()
