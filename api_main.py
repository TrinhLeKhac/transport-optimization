from fastapi import FastAPI
from scripts.api import authen, order, result, zns, output


app = FastAPI(
    title="API SUPERSHIP",
    description="There are APIs getting calculation result from history transactions of SUPERSHIP",
    docs_url="/"
)


app.include_router(authen.router, tags=[""], prefix="/superai/auth")
app.include_router(zns.router, tags=[""], prefix="/superai/zns")
app.include_router(order.router, tags=[""], prefix="/superai/order")
app.include_router(result.router, tags=[""], prefix="/superai/result")
app.include_router(output.router, tags=[""], prefix="/superai/output")

