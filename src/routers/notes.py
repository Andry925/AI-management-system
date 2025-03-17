from fastapi import APIRouter, status, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy_continuum import version_class

from database import db_dependency
from external_services.openai_service import make_summarization
from models.notes_model import Note
from models.user_model import User
from schemas.note_schema import NoteSchema, NoteResponseSchema
from .auth import user_dependency

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=NoteSchema)
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
    note_owner = user_result.scalar_one_or_none()
    note_object = Note(**note_request_dict)
    note_object.user_id = int(user.get('id'))
    note_object.user = note_owner
    db.add(note_object)
    await db.commit()
    await db.refresh(note_object)
    return note_object

@router.get("/", status_code=status.HTTP_200_OK, response_model=list[NoteResponseSchema])
async def get_my_notes(
    db: db_dependency,
    user: user_dependency,
    page: int = Query(1, gt=0),
    per_page: int = Query(10, gt=0)
):
    current_user_id = int(user.get("id"))
    notes_result = await db.execute(
        select(Note)
        .where(Note.user_id == current_user_id)
        .limit(per_page)
        .offset((page - 1) * per_page)
    )
    notes = notes_result.scalars().all()
    return [
        NoteResponseSchema(
            id=note.id,
            user_email=user.get('sub'),
            title=note.title,
            priority=note.priority,
            content=note.content
        ) for note in notes
    ]

@router.get("/{note_id}", status_code=status.HTTP_200_OK, response_model=NoteSchema)
async def get_note(
    db: db_dependency,
    user: user_dependency,
    note_id: int = Path(..., gt=0)
):
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == int(user.get("id")))
    )
    existed_note = result.scalar_one_or_none()
    if not existed_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note with such id does not exist")
    return existed_note

@router.put("/{note_id}", status_code=status.HTTP_200_OK, response_model=NoteSchema)
async def update_note(
    db: db_dependency,
    user: user_dependency,
    note: NoteSchema,
    note_id: int = Path(..., gt=0)
):
    note_request_dict = note.model_dump()
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == int(user.get("id")))
    )
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

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    db: db_dependency,
    user: user_dependency,
    note_id: int = Path(..., gt=0)
):
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == int(user.get("id")))
    )
    existed_note = result.scalar_one_or_none()
    if not existed_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note with such id does not exist")
    await db.delete(existed_note)
    await db.commit()

@router.get("/{note_id}/history", status_code=status.HTTP_200_OK, response_model=list[NoteResponseSchema])
async def get_note_history(
    db: db_dependency,
    user: user_dependency,
    note_id: int = Path(..., gt=0),
    page: int = Query(1, gt=0),
    per_page: int = Query(10, gt=0)
):
    current_user_id = int(user.get("id"))
    NoteVersion = version_class(Note)
    notes_history_result = await db.execute(
        select(NoteVersion)
        .where(NoteVersion.id == note_id, NoteVersion.user_id == current_user_id)
        .limit(per_page)
        .offset((page - 1) * per_page)
    )
    notes_history = notes_history_result.scalars().all()
    return [
        NoteResponseSchema(
            id=note.id,
            user_email=user.get('sub'),
            title=note.title,
            priority=note.priority,
            content=note.content
        ) for note in notes_history
    ]

@router.post("/{note_id}/summarization", status_code=status.HTTP_201_CREATED)
async def summarize_note(
    db: db_dependency,
    user: user_dependency,
    note_id: int = Path(..., gt=0)
):
    current_user_id = int(user.get("id"))
    note_result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == current_user_id)
    )
    note = note_result.scalar_one_or_none()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note with such id does not exist")
    note_summarization = note.summarization
    if note_summarization:
        return JSONResponse(
            content={"summarization": note_summarization},
            status_code=status.HTTP_200_OK
        )
    note_content = note.content
    summarization = await make_summarization(note_content=note_content)
    if not summarization:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate a summarization for the note."
        )
    note.summarization = summarization
    await db.commit()
    await db.refresh(note)
    return JSONResponse(
        content={"summarization": note.summarization},
        status_code=status.HTTP_201_CREATED
    )
