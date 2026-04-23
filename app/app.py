from fastapi import FastAPI,Depends

from app.api import 

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}







