from fastapi import APIRouter

from scripts.api.auth.token import *
from scripts.api.schemas import LoginModel

router = APIRouter()


@router.post("")
def login(request_data: LoginModel):
    print(f"[x] request_data: {request_data.__dict__}")
    if verify_password(username=request_data.username, password=request_data.password):
        token = generate_token(request_data.username, request_data.password)
        return {"error": False, "message": "", "data": {"token": token}}
    else:
        return {
            "error": True,
            "message": "User not found",
            "data": {"token": "Invalid"},
        }
