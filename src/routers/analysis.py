from fastapi import APIRouter
from database import db_dependency
from .auth import user_dependency
from sqlalchemy import select
from models.notes_model import Note
from utils.analysis_utils import Analysis
from schemas.note_schema import NoteSchema

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.get("/notes")
async def create_analysis(db: db_dependency, user: user_dependency):
    current_user_id = int(user.get("id"))
    all_notes_results = await db.execute(select(Note).where(Note.user_id == current_user_id))
    notes_results = all_notes_results.scalars().all()
    result_list = [
        NoteSchema(title=note.title, content=note.content, priority=note.priority).dict()
        for note in notes_results
    ]
    analysis = Analysis(dataset=result_list)
    return analysis.to_dict()
