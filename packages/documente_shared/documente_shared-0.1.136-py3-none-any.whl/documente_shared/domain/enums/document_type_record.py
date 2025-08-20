from src.common.domain.base_enum import BaseEnum

class DocumentTypeRecord(BaseEnum):
    DOCUMENT_PROCESSING = 'DOCUMENT_PROCESSING'
    DOCUMENT_CASE = 'DOCUMENT_CASE'
    
    @property
    def is_document_processing(self):
        return self == DocumentTypeRecord.DOCUMENT_PROCESSING
    
    @property
    def is_document_case(self):
        return self == DocumentTypeRecord.DOCUMENT_CASE
