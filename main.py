from fastapi import FastAPI
from routes import router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, Response


app = FastAPI()
app.include_router(router)

async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"  # Replace "*" with your desired origin or list of allowed origins
    return response

app.middleware('http')(add_cors_header)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
