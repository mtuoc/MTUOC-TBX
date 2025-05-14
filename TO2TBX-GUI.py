import tkinter as tk
from tkinter import filedialog, messagebox
from lxml import etree
from collections import defaultdict
import os

def xml_to_tbx_extended(input_path: str, output_path: str):
    tree = etree.parse(input_path)
    root = tree.getroot()

    nsmap = root.nsmap
    ns = {"ns": nsmap[None]} if None in nsmap else {}

    tbx = etree.Element("tbx")
    body = etree.SubElement(tbx, "body")

    for fitxa in root.findall(".//fitxa", namespaces=ns):
        term_entry = etree.SubElement(body, "termEntry")
        lang_terms = defaultdict(list)

        for denom in fitxa.findall("denominacio", namespaces=ns):
            lang = denom.get("llengua")
            text = denom.text.strip() if denom.text else ""
            if not text:
                continue
            if lang == "cod":
                descrip = etree.SubElement(term_entry, "descrip", type="externalCrossReference")
                descrip.text = text
            else:
                lang_terms[lang].append(text)

        for definicio in fitxa.findall("definicio", namespaces=ns):
            lang = definicio.get("llengua")
            text = definicio.text.strip() if definicio.text else ""
            if text and lang:
                descrip = etree.SubElement(term_entry, "descrip", type="definition")
                descrip.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = lang
                descrip.text = text

        for area in fitxa.findall("areatematica", namespaces=ns):
            text = area.text.strip() if area.text else ""
            if text:
                descrip = etree.SubElement(term_entry, "descrip", type="subjectField")
                descrip.text = text

        for lang, terms in lang_terms.items():
            lang_set = etree.SubElement(term_entry, "langSet", attrib={
                "{http://www.w3.org/XML/1998/namespace}lang": lang
            })
            for term in terms:
                tig = etree.SubElement(lang_set, "tig")
                term_elem = etree.SubElement(tig, "term")
                term_elem.text = term

    tbx_tree = etree.ElementTree(tbx)
    tbx_tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)


# GUI implementation
def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
    if file_path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, file_path)

def select_output_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".tbx", filetypes=[("TBX Files", "*.tbx")])
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
        xml_to_tbx_extended(input_path, output_path)
        messagebox.showinfo("Success", f"TBX file saved to:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Conversion Error", str(e))

# Build GUI
root = tk.Tk()
root.title("XML to TBX Converter")

tk.Label(root, text="Input XML File:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_input_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Output TBX File:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_output_file).grid(row=1, column=2, padx=5, pady=5)

tk.Button(root, text="Convert", command=convert, width=20).grid(row=2, column=0, columnspan=3, pady=15)

root.mainloop()
