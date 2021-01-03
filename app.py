from fastapi import FastAPI
import uvicorn


app = FastAPI()


@app.get("/time")
def gettime():
    return {"dd":"a"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
