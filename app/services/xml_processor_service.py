from lxml import etree
from docx import Document
from io import BytesIO
import zipfile
import olefile
from app.services.translator_service import Translator
from fastapi import HTTPException

class XMLProcessor:
    def __init__(self):
        self.translator = Translator

    def extract_and_translate(self, xml_content, src_lang, tgt_lang):
        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.fromstring(xml_content, parser)
        sentences = []

        for elem in root.iter():
            if elem.text and elem.text.strip():
                sentences.append(elem.text.strip())

        translated_sentences = [self.translator(src_lang, tgt_lang).translate(sentence) for sentence in sentences]

        sentence_index = 0
        for elem in root.iter():
            if elem.text and elem.text.strip():
                elem.text = translated_sentences[sentence_index]
                sentence_index += 1

        return etree.tostring(root, pretty_print=True, encoding='unicode')

    def convert_to_docx(self, xml_content):
        document = Document()
        document.add_paragraph(xml_content)
        file_stream = BytesIO()
        document.save(file_stream)
        file_stream.seek(0)
        return file_stream

    def convert_to_doc(self, xml_content):
        file_stream = BytesIO()
        with olefile.OleFileIO() as ole:
            ole.write_stream('WordDocument', xml_content.encode('utf-8'))
            ole.save(file_stream)
        file_stream.seek(0)
        return file_stream

    def process_and_convert(self, file, src_lang, tgt_lang, output_format):
        if file.filename.endswith('.docx'):
            xml_content = self.extract_xml_from_docx(file.file)
        elif file.filename.endswith('.doc'):
            xml_content = self.extract_xml_from_doc(file.file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        translated_xml = self.extract_and_translate(xml_content, src_lang, tgt_lang)

        if output_format == 'docx':
            file_stream = self.convert_to_docx(translated_xml)
            media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif output_format == 'doc':
            file_stream = self.convert_to_doc(translated_xml)
            media_type = 'application/msword'
        else:
            raise HTTPException(status_code=400, detail="Unsupported output format")

        return file_stream, media_type

    def extract_xml_from_docx(self, file):
        file.seek(0)
        file_content = BytesIO(file.read())
        with zipfile.ZipFile(file_content, 'r') as z:
            xml_content = z.read('word/document.xml')
        return xml_content

    def extract_xml_from_doc(self, file):
        ole = olefile.OleFileIO(file)
        if ole.exists('WordDocument'):
            stream = ole.openstream('WordDocument')
            doc_content = stream.read()
            return f"<xml><content>{doc_content}</content></xml>"
        else:
            raise HTTPException(status_code=400, detail="Unsupported DOC file format")
