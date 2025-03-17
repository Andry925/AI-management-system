import pytest
from sqlalchemy import select

from models.notes_model import Note
from .utils import TestingSession, async_client, create_random_note, create_test_db


@pytest.mark.asyncio
async def test_summarize_note_success(async_client, create_random_note, monkeypatch):
    async def return_random_summary(note_content):
        return "Random summarization"

    monkeypatch.setattr("routers.notes.make_summarization", return_random_summary)
    note = create_random_note
    note_id = note.id
    sum_resp = await async_client.post(f"/api/v1/notes/note/summarization/{note_id}")
    assert sum_resp.status_code == 201
    async with TestingSession() as db:
        result = await db.execute(select(Note).where(Note.id == note_id))
        updated_note = result.scalar_one_or_none()
        assert updated_note is not None
        assert updated_note.summarization == "Random summarization"


@pytest.mark.asyncio
async def test_summarize_note_with_existing_summary(async_client, create_random_note):
    note = create_random_note
    note_id = note.id
    preexisting_summary = "Pre-existing summary."
    async with TestingSession() as db:
        result = await db.execute(select(Note).where(Note.id == note_id))
        note_obj = result.scalar_one_or_none()
        note_obj.summarization = preexisting_summary
        await db.commit()
        await db.refresh(note_obj)

    response = await async_client.post(f"/api/v1/notes/note/summarization/{note_id}")
    assert response.status_code == 200
    data = response.json()
    assert "summarization" in data
    assert data["summarization"] == preexisting_summary


@pytest.mark.asyncio
async def test_summarize_note_not_found(async_client):
    random_id= 3213214
    response = await async_client.post(f"/api/v1/notes/note/summarization/{random_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Note with such id does not exist"
