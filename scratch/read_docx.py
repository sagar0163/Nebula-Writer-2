import sys

import docx2txt


def convert_docx_to_txt(docx_path, txt_path):
    try:
        text = docx2txt.process(docx_path)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Successfully converted {docx_path} to {txt_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    convert_docx_to_txt("docs/AutoNovelist_BRD_v2.1.docx", "scratch/brd_text.txt")
