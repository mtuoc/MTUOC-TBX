import tkinter as tk
from tkinter import filedialog, messagebox
from lxml import etree
import pandas as pd
from collections import defaultdict
import os

def tbx_to_excel(input_path: str, output_path: str):
    tree = etree.parse(input_path)
    root = tree.getroot()

    entries = []

    for term_entry in root.findall(".//termEntry"):
        entry = defaultdict(list)

        for descrip in term_entry.findall("descrip"):
            dtype = descrip.get("type")
            lang = descrip.get("{http://www.w3.org/XML/1998/namespace}lang")
            key = dtype if not lang else f"{dtype}_{lang}"
            if descrip.text:
                entry[key].append(descrip.text.strip())

        for lang_set in term_entry.findall("langSet"):
            lang = lang_set.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lang:
                terms = [term.text.strip() for term in lang_set.findall(".//term") if term.text]
                if terms:
                    entry[lang].extend(terms)

        flat_entry = {k: "; ".join(v) for k, v in entry.items()}
        entries.append(flat_entry)

    df = pd.DataFrame(entries)
    df.fillna("", inplace=True)
    df.to_excel(output_path, index=False)

# GUI Functions
def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("TBX Files", "*.tbx")])
    if file_path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, file_path)

def select_output_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    if file_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, file_path)

def convert():
    input_path = input_entry.get()
    output_path = output_entry.get()

    if not os.path.exists(input_path):
        messagebox.showerror("Error", "Input file does not exist.")
        return

    try:
        tbx_to_excel(input_path, output_path)
        messagebox.showinfo("Success", f"Excel file saved to:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Conversion Error", str(e))

# GUI Layout
root = tk.Tk()
root.title("TBX to Excel Converter")

tk.Label(root, text="Input TBX File:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_input_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Output Excel File:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_output_file).grid(row=1, column=2, padx=5, pady=5)

tk.Button(root, text="Convert", command=convert, width=20).grid(row=2, column=0, columnspan=3, pady=15)

root.mainloop()
