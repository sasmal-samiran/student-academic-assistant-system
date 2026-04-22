import uvicorn
from config import HOST, PORT, RELOAD

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)