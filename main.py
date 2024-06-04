import uvicorn

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check


disable_installed_extensions_check()


app = FastAPI(title="Transaction API", description="The management of the Transaction API")


add_pagination(app)


@app.get("/", description="Main page")
def read_root():
    """
    Healthcheck page definition

    :return: dict: health status
    """
    return {"message": "Welcome to FastAPI project"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
