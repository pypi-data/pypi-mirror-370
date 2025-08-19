# Revornix-Python-Lib

The python package for Revornix API.

📕 API Document: [revornix/api](https://revornix.com/en/docs/features/api)

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Qingyon-AI/Revornix)

## Full Docker App

https://github.com/Qingyon-AI/Revornix

## Introduction

🚀 RoadMap: [RoadMap](https://huaqinda.notion.site/RoadMap-224bbdbfa03380fabd7beda0b0337ea3)

🖥️ Official Website: [https://revornix.com](https://revornix.com)

❤️ Join our community: [Discord](https://discord.com/invite/3XZfz84aPN) | [WeChat](https://github.com/Qingyon-AI/Revornix/discussions/1#discussioncomment-13638435) | [QQ](https://github.com/Qingyon-AI/Revornix/discussions/1#discussioncomment-13638435)

## Installation

```shell
pip install revornix
```

## Usage

### Create Document Label

```python
from revornix import Session, Schema

session = Session(base_url='YOUR_API_PREFIX', api_key='YOUR_API_KEY');
data = Schema.DocumentSchema.LabelAddRequest(
    name="test"
)
res = session.create_document_label(data=data)
```

### Create Section Label

```python
from revornix import Session, Schema

session = Session(base_url='YOUR_API_PREFIX', api_key='YOUR_API_KEY');
data = Schema.SectionSchema.LabelAddRequest(
    name="test"
)
res = session.create_section_label(data=data)
```

### Create Section

```python
from revornix import Session, Schema

session = Session(base_url='YOUR_API_PREFIX', api_key='YOUR_API_KEY');
data = Schema.SectionSchema.SectionCreateRequest(
    title="test",
    description="test",
    public=False,
    cover_id=1,
    labels=[]
)
res = session.create_section(data=data)
```

### Get Mine All Document Labels

```python
from revornix import Session

session = Session(base_url='YOUR_API_PREFIX', api_key='YOUR_API_KEY');
res = session.get_mine_all_document_labels()
```

### Create Quick Note Document

```python
from revornix import Session, Schema

session = Session(base_url='YOUR_API_PREFIX', api_key='YOUR_API_KEY');
data = Schema.DocumentSchema.QuickNoteDocumentParameters(
    content="test",
    sections=[],
    auto_summary=False
)
res = session.create_quick_note_document(data=data)
```

### Create Website Document

```python
from revornix import Session, Schema

session = Session(base_url='YOUR_API_PREFIX', api_key='YOUR_API_KEY');
data = Schema.DocumentSchema.WebsiteDocumentParameters(
    url="https://www.google.com",
    sections=[],
    auto_summary=False
)
res = session.create_website_document(data=data)
```

### Create File Document

```python
from revornix import Session, Schema

session = Session(base_url='YOUR_API_PREFIX', api_key='YOUR_API_KEY');
data = Schema.DocumentSchema.FileDocumentParameters(
    file_name="demo",
    sections=[],
    auto_summary=False
)
res = session.create_file_document(data=data)
```

## Contributors

<a href="https://github.com/Qingyon-AI/Revornx/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Qingyon-AI/Revornix" />
</a>