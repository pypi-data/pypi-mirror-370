import os
from dotenv import load_dotenv
load_dotenv(override=True)

import revornix.schema.document as DocumentSchema
import revornix.schema.section as SectionSchema
from revornix.core import Session

base_url = os.environ.get('REVORNIX_URL_PREFIX')
api_key = os.environ.get('API_KEY')

session = Session(base_url=base_url, api_key=api_key)
    
def test_create_file_document():
    data = DocumentSchema.FileDocumentParameters(
        file_name="demo",
        sections=[],
        auto_summary=False
    )
    res = session.create_file_document(data=data)
    assert res is not None
    
def test_create_website_document():
    data = DocumentSchema.WebsiteDocumentParameters(
        url="https://www.google.com",
        sections=[],
        auto_summary=False
    )
    res = session.create_website_document(data=data)
    assert res is not None
    
def test_create_quick_note_document():
    data = DocumentSchema.QuickNoteDocumentParameters(
        content="test",
        sections=[],
        auto_summary=False
    )
    res = session.create_quick_note_document(data=data)
    assert res is not None
    
def test_create_document_label():
    data = DocumentSchema.LabelAddRequest(
        name="test"
    )
    res = session.create_document_label(data=data)
    assert res is not None
    
def test_create_section_label():
    data = SectionSchema.LabelAddRequest(
        name="test"
    )
    res = session.create_section_label(data=data)
    assert res is not None
    
def test_create_section():
    data = SectionSchema.SectionCreateRequest(
        title="test",
        description="test",
        public=False,
        cover_id=1,
        labels=[]
    )
    res = session.create_section(data=data)
    assert res is not None

def test_get_mine_all_document_labels():
    res = session.get_mine_all_document_labels()
    assert res is not None
    
def test_get_mine_all_sections():
    res = session.get_mine_all_sections()
    assert res is not None