import fitz

def extract_text_from_pdf(uploaded_pdf_file):
    '''
    Extract raw text from uploaded PDF resume 
    Input - PDF file uploaded via streamlit
    output - plain text string
    '''
    try:
        doc = fitz.open(
            stream=uploaded_pdf_file.read(),
            filetype="pdf"
            )
        text = ""
        for page in doc:
            text = text + page.get_text()
            
        text = text.strip()
        text = ' '.join(text.split())
        
        if not text:
            raise ValueError(
                "No text found in pdf.")
            
        print(f"PDF extracted successfully - {len(text)} characters")
        return text 
    
    except Exception as e:
        raise RuntimeError(f"Error extracting text from pdf: {e}")
        
        
    
    
        
    
    