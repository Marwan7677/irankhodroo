from fastapi import FastAPI

# ایجاد نمونه برنامه FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World from FastAPI on Vercel!"}

@app.get("/health")
def health():
    return {"status": "ok"}

# اگر مسیر دیگری نیاز دارید، مثلاً دریافت پارامتر
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}
