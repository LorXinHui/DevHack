import tensorflow as tf
from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output
from PIL import Image
import cv2
import re

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'


def get_text(resume_path):
    res = ""
    images = convert_from_path(resume_path, poppler_path='C:/Python311/Lib/poppler-23.11.0/Library/bin')

    for i in range(len(images)):
        text = pytesseract.image_to_string(images[i], lang='eng')
        data = pytesseract.image_to_data(images[i])
        res += text

    return res


def preprocess_paragraph(paragraph):
    # Remove newlines
    paragraph = paragraph.replace('\n', ' ')

    # Remove connectors
    connectors = ['and', 'but', 'or', 'summary', 'experience', 'professional', 'skills', 'profile', 'education',
                  'skill', 'highlights']
    for connector in connectors:
        paragraph = re.sub(r'\b' + re.escape(connector) + r'\b', '', paragraph, flags=re.IGNORECASE)

    # Remove extra spaces
    paragraph = ' '.join(paragraph.split())

    return paragraph


# Load the saved model
model_path = './model'
category = tf.keras.models.load_model(model_path)


def predict_class(resume):
    resume_text = get_text(resume)
    resume_clean = preprocess_paragraph(resume_text)
    predictions = category.predict([resume_clean])
    predicted_class = tf.argmax(predictions[0]).numpy()
    return predicted_class


if __name__ == '__main__':
    resume_path = 'C:/Clubs and Society/DevHack/DevHack/dataset/data/data/ENGINEERING/17108676.pdf'
    print(predict_class(resume_path))
