from fastapi import FastAPI,Depends



app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}







