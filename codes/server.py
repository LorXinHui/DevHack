import re
from pdf2image import convert_from_path
import pytesseract
import tensorflow as tf
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'

def get_resume_text(resume_path):
    res = ""
    images = convert_from_path(resume_path, poppler_path = 'C:/Python311/Lib/poppler-23.11.0/Library/bin')
    for i in range(len(images)):
        text = pytesseract.image_to_string(images[i], lang='eng')
        res += text
    return res

def preprocess_resume(paragraph):
    # Remove newlines
    paragraph = paragraph.replace('\n', ' ')

    # Remove connectors
    connectors = ['and', 'but', 'or', 'summary', 'experience', 'professional', 'skills', 'profile', 'education', 'skill', 'highlights']
    for connector in connectors:
        paragraph = re.sub(r'\b' + re.escape(connector) + r'\b', '', paragraph, flags=re.IGNORECASE)

    # Remove extra spaces
    paragraph = ' '.join(paragraph.split())

    return paragraph

category_model = tf.saved_model.load('./category_model')

def predict_class(resume_path):
    resume_text = get_resume_text(resume_path)
    cleaned_resume = preprocess_resume(resume_text)
    predictions = category_model.predict([cleaned_resume])
    predicted_class = tf.argmax(predictions[0]).numpy
    return predicted_class

if __name__ == "__main__":
    path = 'C:/Clubs and Society/DevHack/DevHack/dataset/data/data/ENGINEERING/17108676.pdf'
    print(predict_class(path))
# End-of-file (EOF)