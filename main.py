import hashlib
from typing import Annotated

from fastapi import FastAPI, Request, Form, Response, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from db import init_db

app = FastAPI()

con = init_db()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def show_feed(request: Request, session_id: Annotated[str | None, Cookie()] = None):

    query = """
        SELECT * FROM posts ORDER BY post_time DESC;
    """
    cur = con.cursor()
    res = cur.execute(query)
    posts = res.fetchall()

    if session_id:
        username = session_id
    else:
        username = None

    context = {"posts": posts, "username": username}

    return templates.TemplateResponse(
        request=request, name="index.html", context=context
    )


@app.post("/posts")
def write_post(request: Request, response: Response, input: str = Form(...)):

    username = request.cookies.get("session_id")
    if not username:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    query = "INSERT INTO posts (content, username) VALUES (?, ?);"

    data = (input, username,)

    cur = con.cursor()
    cur.execute(query, data)
    con.commit()

    response.headers["HX-Refresh"] = "true"

    # return {"message": "successfully made post!"}


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
def login(response: Response, username: str = Form(...), password: str = Form(...)):

    if isinstance(username, str):

        hashed_password_hex = hashlib.sha256(password.encode()).hexdigest()
        
        query = "SELECT * FROM users WHERE hashed_password = ? AND username = ?;"
        
        cur = con.cursor()
        result = cur.execute(query, (hashed_password_hex, username))
        print(cur)
        print(result)
        row_result = result.fetchone()
        print(f"row_result: {row_result}")
        print(f"password, '{password}'")
        print(f"hashed_password, '{hashed_password_hex}'")
        print(f"username, '{username}'")

        if row_result:
            response.set_cookie(key="session_id", value=username, max_age=3600, path="/")
            response.headers["HX-Refresh"] = "true"
        elif not row_result:
            return RedirectResponse("/signup", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return {"error": "failed to log in, refresh to try again"}
    
    else:
        return {"message": "failed to log in, refresh to try again"}


@app.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="signup.html"
    )


@app.post("/signup")
def signup(username: str = Form(...), password: str = Form(...)):
    
    if isinstance(username, str) and isinstance(password, str):

        hashed_password_hex = hashlib.sha256(password.encode()).hexdigest()
        query = "INSERT INTO users (username, hashed_password) VALUES (?, ?)"
        cur = con.cursor()
        cur.execute(query, (username, hashed_password_hex,))
        con.commit()
        print(f"password, '{password}'")
        print(f"hashed_password, '{hashed_password_hex}'")
        print(f"username, '{username}'")

        return {"message": "successfully signed up"}

    else:
        return {"error": "failed to sign up"}


@app.post("/logout")
def logout(response: Response):

    response.delete_cookie(key="session_id", path="/")
    response.headers["HX-Refresh"] = "true"
    # return {"message": "deleted cookie"}

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True)
