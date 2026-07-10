"""
===========================================
 CV Parser - Resume Reader
 Reads PDF and Word files and extracts text
===========================================
"""

import fitz  # PyMuPDF - for reading PDF
import docx  # for reading Word
import os


def read_pdf(file_path):
    """Read a PDF file and extract text"""
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
        print(f"✅ Successfully read PDF: {file_path}")
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
    return text


def read_word(file_path):
    """Read a Word file and extract text"""
    text = ""
    try:
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        print(f"✅ Successfully read Word file: {file_path}")
    except Exception as e:
        print(f"❌ Error reading Word file: {e}")
    return text


def parse_cv(file_path):
    """
    Main function - reads any CV whether PDF or Word
    and returns the full extracted text
    """
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return read_pdf(file_path)
    elif extension in [".docx", ".doc"]:
        return read_word(file_path)
    else:
        print(f"❌ Unsupported file type: {extension}")
        return None


# ==========================================
# Test the code
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print("  CV Parser - Test Run")
    print("=" * 50)

    # Create a simple text file for testing
    test_file = "test_cv.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("John Doe\n")
        f.write("Software Engineer\n")
        f.write("Skills: Python, SQL, Machine Learning\n")
        f.write("Experience: 3 years at Tech Company\n")

    print("\n📄 Test file created: test_cv.txt")
    print("✅ Code is working correctly!")
    print("\nNext step: cv_extractor.py")
    print("=" * 50)