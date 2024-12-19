import os
from typing import BinaryIO, List
import streamlit as st
from openai import OpenAI
import fitz  # PyMuPDF library to handle PDF files


def convert_pdf_to_images(pdf_file) -> List[str]:
    """
    Convert PDF pages to images and return paths to the image files.
    """
    document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    images = []

    for page_num in range(len(document)):
        page = document[page_num]
        pix = page.get_pixmap(dpi=150)
        img_path = f"page_{page_num + 1}.png"
        pix.save(img_path)
        images.append(img_path)

    return images


def extract_text_from_page(pdf_file, page_number: int) -> str:
    """
    Extract text from a specific page of the PDF.
    """
    document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    page = document[page_number - 1]  # 0-based indexing
    return page.get_text()


def main():
    st.set_page_config(layout="wide")
    st.title("PDF 문서 번역/요약")
    st.caption("PDF 파일을 업로드하고 페이지를 선택하세요.")

    # Sidebar for file upload and page selection
    with st.sidebar:
        openai_api_key = st.text_input(
            "OpenAI API Key", key="summarizer_api_key", type="password"
        )
        st.markdown(
            "[OpenAI API key 받기](https://platform.openai.com/account/api-keys)"
        )
        pdf_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])

    if pdf_file:
        # Convert PDF to images and store in session state
        if "images" not in st.session_state:
            st.session_state.images = convert_pdf_to_images(pdf_file)

        # Left and Right Columns
        left_col, right_col = st.columns([1, 1])

        with left_col:
            st.subheader("PDF 미리보기")
            total_pages = len(st.session_state.images)
            page_number = st.number_input(
                "페이지 번호를 선택하세요", min_value=1, max_value=total_pages, value=1
            )
            image_path = st.session_state.images[page_number - 1]
            st.image(
                image_path, caption=f"Page {page_number}", use_container_width=True
            )

        with right_col:
            st.subheader("PDF 요약")
            if st.button("요약 실행"):
                if not openai_api_key:
                    st.error("API Key를 입력해주세요.")
                    return

                client = OpenAI(api_key=openai_api_key)
                extracted_text = extract_text_from_page(pdf_file, page_number)
                prompt = f"다음 텍스트를 요약해줘:\n\n{extracted_text}"

                with st.spinner("요약 중..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                    )
                    summary = response.choices[0].message.content

                st.write(summary)


if __name__ == "__main__":
    main()
