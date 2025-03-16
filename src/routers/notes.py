from fastapi import APIRouter, status, HTTPException, Path
from sqlalchemy import select
from sqlalchemy_continuum import version_class

from database import db_dependency
from models.notes_model import Note
from models.user_model import User
from schemas.note_schema import NoteSchema, NoteResponseSchema, NoteUpdateSchema
from .auth import user_dependency

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])


@router.post("/new-note",
             status_code=status.HTTP_201_CREATED,
             response_model=NoteSchema)
async def create_note(db: db_dependency, user: user_dependency, note: NoteSchema):
    note_request_dict = note.model_dump()
    title = note_request_dict["title"]
    result = await db.execute(select(Note).where(Note.title == title))
    existed_note = result.scalar_one_or_none()
    if existed_note:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note already exists")
    user_result = await db.execute(select(User).where(User.id == int(user.get("id"))))
    user = user_result.scalar_one_or_none()
    note_object = Note(**note_request_dict)
    note_object.user_id = int(user.id)
    note_object.user = user
    db.add(note_object)
    await db.commit()
    await db.refresh(note_object)
    return note_object


@router.get("/my-notes/{page}/{per_page}",
            status_code=status.HTTP_200_OK,
            response_model=list[NoteResponseSchema])
async def get_my_notes(db: db_dependency, user: user_dependency, page: int = Path(gt=0), per_page: int = Path(gt=0)):
    current_user_id = int(user.get("id"))
    notes_result = await db.execute(select(Note).where(Note.user_id == current_user_id).limit(
        per_page).offset((page - 1) * per_page))
    notes = notes_result.scalars().all()
    return [
        NoteResponseSchema(
            id=note.id,
            user_email=user.get('sub'),
            title=note.title,
            priority=note.priority,
            content=note.content) for note in notes]


@router.put("/note-update/{note_id}",
            status_code=status.HTTP_200_OK,
            response_model=NoteUpdateSchema)
async def update_note(db: db_dependency, user: user_dependency, note: NoteSchema, note_id: int = Path(gt=0)):
    note_request_dict = note.model_dump()
    result = await db.execute(select(Note).where(Note.id == note_id, Note.user_id == int(user.get("id"))))
    existed_note = result.scalar_one_or_none()
    if not existed_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note does not exist")
    for key, value in note_request_dict.items():
        setattr(existed_note, key, value)
    await db.commit()
    await db.refresh(existed_note)
    return existed_note


@router.delete("/delete-note/{note_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(db: db_dependency, user: user_dependency, note_id: int = Path(..., gt=0)):
    result = await db.execute(select(Note).where(Note.id == note_id, Note.user_id == int(user.get("id"))))
    existed_note = result.scalar_one_or_none()
    if not existed_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note with such id does not exist")
    await db.delete(existed_note)
    await db.commit()


@router.get("/single-note/{note_id}",
            status_code=status.HTTP_200_OK,
            response_model=NoteResponseSchema)
async def get_note(db: db_dependency, user: user_dependency, note_id: int = Path(gt=0)):
    result = await db.execute(select(Note).where(Note.id == note_id, Note.user_id == int(user.get("id"))))
    existed_note = result.scalar_one_or_none()
    if not existed_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note with such id does not exist")
    return existed_note


@router.get("/note/history/{note_id}/{page}/{per_page}",
            status_code=status.HTTP_200_OK,
            response_model=list[NoteResponseSchema])
async def get_note_history(db: db_dependency, user: user_dependency, note_id: int = Path(gt=0), page: int = Path(gt=0),
                           per_page: int = Path(gt=0)):
    current_user_id = int(user.get("id"))
    NoteVersion = version_class(Note)
    notes_history_result = await db.execute(
        select(NoteVersion).where(NoteVersion.id == note_id, NoteVersion.user_id == current_user_id).limit(
            per_page).offset((page - 1) * per_page))
    notes_history = notes_history_result.scalars().all()
    return [
        NoteResponseSchema(
            id=note.id,
            user_email=user.get('sub'),
            title=note.title,
            priority=note.priority,
            content=note.content) for note in notes_history]
