from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from field_types import DocumentTypes
from Entries.models import EntryType

if TYPE_CHECKING:
    from Entries.models import DrEntries, CrEntries

class JournalBase(SQLModel):
    doc_date:date
    doc_prefix:str = "V-"
    doc_number:int
    doc_type:DocumentTypes
    narration:Optional[str]

class Journals(JournalBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    timestamp:datetime = datetime.utcnow()
    dr_entries:Optional[List["DrEntries"]] = Relationship(back_populates='journal')
    cr_entries:Optional[List["CrEntries"]] = Relationship(back_populates='journal')
    status:bool = Field(default=True)
    master_entry_type:EntryType