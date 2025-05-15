import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from lxml import etree
import os

def tsv_to_tbx(input_path: str, output_path: str):
    df = pd.read_csv(input_path, sep="\t", dtype=str).fillna("")

    tbx = etree.Element("tbx")
    body = etree.SubElement(tbx, "body")

    for _, row in df.iterrows():
        term_entry = etree.SubElement(body, "termEntry")

        for col, val in row.items():
            if not val:
                continue
            if col.startswith("definition_"):
                lang = col.replace("definition_", "")
                for definition in val.split("; "):
                    descrip = etree.SubElement(term_entry, "descrip", type="definition")
                    descrip.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = lang
                    descrip.text = definition
            elif col == "externalCrossReference":
                for ref in val.split("; "):
                    descrip = etree.SubElement(term_entry, "descrip", type="externalCrossReference")
                    descrip.text = ref
            elif col == "subjectField":
                for subject in val.split("; "):
                    descrip = etree.SubElement(term_entry, "descrip", type="subjectField")
                    descrip.text = subject
            else:
                lang_set = etree.SubElement(term_entry, "langSet", attrib={
                    "{http://www.w3.org/XML/1998/namespace}lang": col
                })
                for term in val.split("; "):
                    tig = etree.SubElement(lang_set, "tig")
                    term_elem = etree.SubElement(tig, "term")
                    term_elem.text = term

    etree.ElementTree(tbx).write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)

# Interfaz gráfica
def select_input_file():
    path = filedialog.askopenfilename(filetypes=[("TSV files", "*.tsv")])
    if path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, path)

def select_output_file():
    path = filedialog.asksaveasfilename(defaultextension=".tbx", filetypes=[("TBX files", "*.tbx")])
    if path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, path)

def convert():
    input_path = input_entry.get()
    output_path = output_entry.get()
    if not os.path.exists(input_path):
        messagebox.showerror("Error", "Input file does not exist.")
        return
    try:
        tsv_to_tbx(input_path, output_path)
        messagebox.showinfo("Success", f"TBX file saved to:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Conversion failed", str(e))

root = tk.Tk()
root.title("TSV to TBX Converter")

tk.Label(root, text="Input TSV File:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_input_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Output TBX File:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_output_file).grid(row=1, column=2, padx=5, pady=5)

tk.Button(root, text="Convert", command=convert, width=20).grid(row=2, column=0, columnspan=3, pady=15)

root.mainloop()
