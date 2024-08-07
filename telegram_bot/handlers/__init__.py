from .start import register_handlers_start
from .document import register_handlers_document
from .translation import register_handlers_translation

def register_handlers(dp):
    register_handlers_start(dp)
    register_handlers_document(dp)
    register_handlers_translation(dp)
