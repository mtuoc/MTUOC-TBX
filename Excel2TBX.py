import argparse
import pandas as pd
from lxml import etree

def excel_to_tbx(input_path: str, output_path: str):
    df = pd.read_excel(input_path)
    df.fillna("", inplace=True)

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
                # Asumir que es una lengua
                lang_set = etree.SubElement(term_entry, "langSet", attrib={
                    "{http://www.w3.org/XML/1998/namespace}lang": col
                })
                for term in val.split("; "):
                    tig = etree.SubElement(lang_set, "tig")
                    term_elem = etree.SubElement(tig, "term")
                    term_elem.text = term

    tree = etree.ElementTree(tbx)
    tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    print(f"TBX file successfully written to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Excel file to TBX.")
    parser.add_argument("-i", "--input", required=True, help="Path to input Excel file (.xlsx)")
    parser.add_argument("-o", "--output", required=True, help="Path to output TBX file (.tbx)")
    args = parser.parse_args()

    excel_to_tbx(args.input, args.output)
