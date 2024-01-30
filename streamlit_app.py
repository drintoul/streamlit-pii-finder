import streamlit as st
#st.set_page_config(layout="wide")

from pdf2image import convert_from_bytes
from PIL import Image
from PyPDF2 import PdfReader

from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()

def find_pii(text):

    results = analyzer.analyze(text=text, entities=[], language='en', score_threshold=0.5)

    pii = {}

    for item in results:

        parsed = str(item).split(',')
        type = parsed[0].split()[1]
        start = int(parsed[1].split()[1])
        end = int(parsed[2].split()[1])

        if type in pii.keys():
            pii[type].append(text[start:end])
        else:
            pii[type] = [text[start:end]]

    return pii

def read_pdf_page(file, page_number):

    pdfReader = PdfReader(file)
    page = pdfReader.pages[page_number]
    text = page.extract_text()

    return find_pii(text)

def on_text_area_change():

    st.session_state.page_text = st.session_state.my_text_area

def main():

    st.set_page_config(page_title="Resume Highlighter")
    st.title("Resume Highlighter")

    # PDF file upload
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if pdf_file:

        # Create a selectbox to choose the page number
        pdfReader = PdfReader(pdf_file)
        page_numbers = list(range(1, len(pdfReader.pages)+1))
        selected_page = st.selectbox("Select a page", page_numbers)
        selected_page -= 1

        # Convert the selected page to an image
        images = convert_from_bytes(pdf_file.getvalue())
        image = images[selected_page]

        # Create two columns to display the image and text
        col1, col2 = st.columns(2)

        # Display the image in the first column
        col1.image(image, caption=f"Page {selected_page + 1}")

        col2.text_area("Extracted Text", height=400, value=read_pdf_page(pdf_file, selected_page),
                       key="my_text_area", on_change=on_text_area_change)

if __name__ == '__main__':
    main()
