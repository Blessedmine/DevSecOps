from fastapi import FastAPI, HTTPException

app = FastAPI(title="DevSecOps Demo API")

ITEMS = {
    1: {"name": "Widget", "price": 9.99},
    2: {"name": "Gadget", "price": 24.99},
}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    return ITEMS[item_id]