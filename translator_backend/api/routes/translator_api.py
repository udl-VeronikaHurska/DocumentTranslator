from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from api.services.xml_processor_service import XMLProcessor

router = APIRouter()

@router.post("/translate_document", response_description="Download translated document")
async def translate_document(file: UploadFile = File(...), src_lang: str = 'german', tgt_lang: str = 'ukrainian', output_format: str = 'docx'):
    xml_processor = XMLProcessor()
    try:
        output_stream, media_type = xml_processor.process_and_convert(file, src_lang, tgt_lang, output_format)
        
        filename = f"translated_document.{output_format}"
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': media_type
        }
        
        return StreamingResponse(output_stream, headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
