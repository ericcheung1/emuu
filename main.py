from fastapi import FastAPI, Request, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
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
def write_post(request: Request, input: str = Form(...)):

    username = request.cookies.get("session_id")
    if not username:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    query = "INSERT INTO posts (content, username) VALUES (?, ?);"

    data = (input, username,)

    cur = con.cursor()
    cur.execute(query, data)
    con.commit()

    return {"message": "successfully made post!"}


@app.get("/posts", response_class=HTMLResponse)
def post_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="posts.html"
    )


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html"
    )


@app.post("/login")
def login(response: Response, username: str = Form(...)):

    if isinstance(username, str):
        response.set_cookie(key="session_id", value=username, max_age=3600, path="/")
        return {"message": "successfully logged in"}
    else:
        return {"message": "failed to log in"}


@app.post("/logout")
def logout(response: Response):

    response.delete_cookie(key="session_id", path="/")

    return {"message": "deleted cookie"}

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True)
