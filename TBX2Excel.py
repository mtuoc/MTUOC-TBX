import argparse
from lxml import etree
import pandas as pd
from collections import defaultdict

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
    print(f"Excel file successfully written to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert enriched TBX file to Excel.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input TBX file.")
    parser.add_argument("-o", "--output", required=True, help="Path to the output Excel (.xlsx) file.")
    args = parser.parse_args()

    tbx_to_excel(args.input, args.output)
