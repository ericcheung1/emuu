from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from db import init_db

app = FastAPI()

con = init_db()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def show_feed(request: Request, response_class=HTMLResponse):

    query = """
        SELECT * FROM posts ORDER BY post_time DESC;

    """
    cur = con.cursor()
    res = cur.execute(query)
    posts = res.fetchall()

    context = {"posts": posts}

    return templates.TemplateResponse(
        request=request, name="index.html", context=context
    )


@app.post("/posts")
def write_post(request: Request, input: str = Form(...), username: str = Form(...)):
    query = "INSERT INTO posts (content, username) VALUES (?, ?);"

    data = (input, username,)

    cur = con.cursor()
    cur.execute(query, data)
    con.commit()

    return {"response": "successfully made post!"}


@app.get("/posts", response_class=HTMLResponse)
def post_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="posts.html"
    )

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True)
