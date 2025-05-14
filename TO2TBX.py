import argparse
from lxml import etree
from collections import defaultdict

def xml_to_tbx_extended(input_path: str, output_path: str):
    tree = etree.parse(input_path)
    root = tree.getroot()

    # Detect namespace if present
    nsmap = root.nsmap
    ns = {"ns": nsmap[None]} if None in nsmap else {}

    tbx = etree.Element("tbx")
    body = etree.SubElement(tbx, "body")

    for fitxa in root.findall(".//fitxa", namespaces=ns):
        term_entry = etree.SubElement(body, "termEntry")
        lang_terms = defaultdict(list)

        # IATE codes
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

        # Definitions
        for definicio in fitxa.findall("definicio", namespaces=ns):
            lang = definicio.get("llengua")
            text = definicio.text.strip() if definicio.text else ""
            if text and lang:
                descrip = etree.SubElement(term_entry, "descrip", type="definition")
                descrip.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = lang
                descrip.text = text

        # Subject fields
        for area in fitxa.findall("areatematica", namespaces=ns):
            text = area.text.strip() if area.text else ""
            if text:
                descrip = etree.SubElement(term_entry, "descrip", type="subjectField")
                descrip.text = text

        # Terms by language
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
    print(f"TBX file successfully written to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a TERMCAT-style XML file to TBX enriched format."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to the input XML file."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to the output TBX file."
    )

    args = parser.parse_args()
    xml_to_tbx_extended(args.input, args.output)
