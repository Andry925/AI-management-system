import pytest

from .utils import async_client, create_random_note, create_test_db, INITIAL_NOTE_DATA

NOTE_DATA = {
    "title": "Unique Test Note",
    "content": "This is a test note content.",
    "priority": 5,
    "user_id": 1
}

NEW_NOTE = {
    "title": "New Test Note",
    "content": "This is a test note content.",
    "priority": 5,
}

UPDATED_NOTE_DATA = {
    "title": "Updated Test Note",
    "content": "This is updated test note content.",
    "priority": 3
}


@pytest.mark.asyncio
async def test_create_note(async_client):
    response = await async_client.post("/api/v1/notes/", json=NOTE_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == NOTE_DATA["title"]
    assert data["content"] == NOTE_DATA["content"]
    assert data["priority"] == NOTE_DATA["priority"]


@pytest.mark.asyncio
async def test_create_note_already_exists(async_client, create_random_note):
    response = await async_client.post("/api/v1/notes/", json=NOTE_DATA)
    assert response.status_code == 400
    assert response.json()["detail"] == "Note already exists"


@pytest.mark.asyncio
async def test_get_my_notes(async_client, create_random_note):
    response = await async_client.post("/api/v1/notes/", json=NEW_NOTE)
    assert response.status_code == 201
    get_response = await async_client.get("/api/v1/notes/?page=1&per_page=10")
    assert get_response.status_code == 200
    notes = get_response.json()
    assert isinstance(notes, list)
    assert len(notes) == 2


@pytest.mark.asyncio
async def test_update_note(async_client, create_random_note):
    note = create_random_note
    note_id = note.id
    update_resp = await async_client.put(f"/api/v1/notes/{note_id}", json=UPDATED_NOTE_DATA)
    assert update_resp.status_code == 200
    updated_note = update_resp.json()
    assert updated_note["title"] == UPDATED_NOTE_DATA["title"]
    assert updated_note["content"] == UPDATED_NOTE_DATA["content"]
    assert updated_note["priority"] == UPDATED_NOTE_DATA["priority"]


@pytest.mark.asyncio
async def test_update_non_existent_note(async_client, create_random_note):
    invalid_id = 343432
    update_fail = await async_client.put(f"/api/v1/notes/{invalid_id}", json=UPDATED_NOTE_DATA)
    assert update_fail.status_code == 404
    assert update_fail.json()["detail"] == "Note does not exist"


@pytest.mark.asyncio
async def test_delete_note(async_client, create_random_note):
    note = create_random_note
    note_id = note.id
    response = await async_client.delete(f"/api/v1/notes/{note_id}")
    assert response.status_code == 204
    response_after_deletion = await async_client.get(f"/api/v1/notes/{note_id}")
    assert response_after_deletion.status_code == 404
    assert response_after_deletion.json()["detail"] == "Note with such id does not exist"


@pytest.mark.asyncio
async def test_get_single_note(async_client, create_random_note):
    note = create_random_note
    note_id = note.id
    response = await async_client.get(f"/api/v1/notes/{note_id}")
    assert response.status_code == 200
    fetched_note = response.json()
    assert fetched_note["title"] == INITIAL_NOTE_DATA["title"]
    assert fetched_note["content"] == INITIAL_NOTE_DATA["content"]


@pytest.mark.asyncio
async def test_get_note_history(async_client, create_random_note):
    note = create_random_note
    note_id = note.id
    update_request = {"title": "some new title", "content": "More content", "priority": 8}
    response = await async_client.put(f"/api/v1/notes/{note_id}", json=update_request)
    assert response.status_code == 200
    history_resp = await async_client.get(f"/api/v1/notes/{note_id}/history?page=1&per_page=10")
    assert history_resp.status_code == 200
    history_list = history_resp.json()
    assert isinstance(history_list, list)
    print(history_list)
    assert len(history_list) > 1
    first_history = history_list[0]
    assert "title" in first_history
    assert "content" in first_history
    assert "priority" in first_history
