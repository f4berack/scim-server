import uuid 
import json
import fakeredis

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from model import Meta, ScimCreateUserRequest, ScimUser, SCIM_USER_SCHEMA, SCIM_ERROR_SCHEMA
from ldap_server import add_user_entry, get_user_entry, delete_user_entry

from datetime import datetime
from zoneinfo import ZoneInfo

app = FastAPI(title="f4berack scim-showcase", version="1.0")

r = fakeredis.FakeRedis(decode_response=True)

@app.post("/Users", status_code=status.HTTP_201_CREATED)
def create_user(payload: ScimCreateUserRequest):
    
    user_id = str(uuid.uuid4())
    now_formatted_datetime = datetime.now(ZoneInfo("UTC")).strftime('%Y-%m-%dT%H:%M:%SZ')

    user = ScimUser(
        schemas=[SCIM_USER_SCHEMA],
        id=user_id,
        externalId=payload.externalId,
        meta=Meta(
            resourceType="User",
            created=now_formatted_datetime,
            lastModified=now_formatted_datetime,
            location=f"https://example.com/Users/{user_id}",
            version="v1.0"
        ),
        name=payload.name,
        userName=payload.userName
    )

    r.set(user_id, user.json())

    add_user_entry(user)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=user.model_dump(),
        headers={
            "Location": f"https://example.com/Users/{user_id}"
        }
    )

@app.get("/Users/{id}", status_code=status.HTTP_200_OK)
async def get_user(id):

    if not r.exists(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {id} does not exist")

    user_entry = r.get(id)

    get_user_entry(id)

    return json.loads(user_entry)

@app.put("/Users/{id}")
async def substitute_user(id):
    pass

@app.patch("/Users/{id}")
async def edit_user(id):
    pass

@app.delete("/Users/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id):
    
    deleted = r.delete(id)

    delete_user_entry(id)
    
    if deleted == 0:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    return Response(status_code=status.HTTP_204_NO_CONTENT)