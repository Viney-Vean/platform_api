from app.main import app, apm


@app.get("/")
async def root():
    try:
        1 / 0
    except ZeroDivisionError:
        apm.capture_exception()
        pass
    return {"message": "Hello World"}
