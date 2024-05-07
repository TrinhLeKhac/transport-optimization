from scripts.api.router import api_output, order, zns, optimal_score, result, result_final, result_super
from scripts.api.auth import authen
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, status, Depends
from ast import literal_eval
from fastapi.responses import JSONResponse

from scripts.api.auth.security import validate_token

app = FastAPI(
    title="API SUPERSHIP",
    description="There are APIs getting calculation result from history transactions of SUPERSHIP",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


def create_str_err(exc_str):
    errs = literal_eval(exc_str)
    res = []
    for err in errs:
        s = str(err["loc"]) + " => " + err["msg"]
        res.append(s)
    return "; ".join(res)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    path = request.url.path
    if path == "/superai/auth":
        content = {"error": True, "message": create_str_err(exc_str), "data": {"token": "Invalid"}}
    else:
        content = {"error": True, "message": create_str_err(exc_str), "data": []}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


app.include_router(authen.router, tags=[""], prefix="/superai/auth")
app.include_router(zns.router, tags=[""], prefix="/superai/zns", dependencies=[Depends(validate_token)])
app.include_router(order.router, tags=[""], prefix="/superai/order", dependencies=[Depends(validate_token)])
app.include_router(result.router, tags=[""], prefix="/superai/result", dependencies=[Depends(validate_token)])
app.include_router(result_final.router, tags=[""], prefix="/superai/final", dependencies=[Depends(validate_token)])
app.include_router(result_super.router, tags=[""], prefix="/superai/super", dependencies=[Depends(validate_token)])
app.include_router(api_output.router, tags=[""], prefix="/superai/district", dependencies=[Depends(validate_token)])
app.include_router(optimal_score.router, tags=[""], prefix="/superai/score", dependencies=[Depends(validate_token)])