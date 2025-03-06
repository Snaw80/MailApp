from fastapi import FastAPI

app = FastAPI()

item = ["apple", "banana", "cherry"]

def get_item(item_id: int):
    if item_id < 0 or item_id >= len(item):
        return None
    return item[item_id]

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    q = get_item(item_id)
    return {"item_id": item_id, "q": q}

# Run the server
# Command to run: `uvicorn test:app --reload`