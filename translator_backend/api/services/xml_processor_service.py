from lxml import etree
from docx import Document
from io import BytesIO
import zipfile
import olefile
from api.services.translator_service import Translator
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

        return etree.tostring(root, pretty_print=True, encoding='utf-8')

    def convert_to_docx(self, xml_content):
        file_stream = BytesIO()
        with zipfile.ZipFile(file_stream, 'w') as z:
            z.writestr('word/document.xml', xml_content)
            # Add all necessary DOCX parts here (content_types, rels, etc.)
            z.writestr('[Content_Types].xml', self.get_content_types())
            z.writestr('_rels/.rels', self.get_rels())
            z.writestr('word/_rels/document.xml.rels', self.get_word_rels())
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
        else:
            raise HTTPException(status_code=400, detail="Unsupported output format")

        return file_stream, media_type

    def extract_xml_from_docx(self, file):
        file.seek(0)
        file_content = BytesIO(file.read())
        with zipfile.ZipFile(file_content, 'r') as z:
            xml_content = z.read('word/document.xml')
        return xml_content

    def get_content_types(self):
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''

    def get_rels(self):
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

    def get_word_rels(self):
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>'''
