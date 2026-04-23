from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/{id}")
def get_it(id:int):
    return {"items":"item id is {id}"}
