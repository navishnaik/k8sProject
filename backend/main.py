from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import psycopg2
from pydantic import BaseModel
import os
import time
from prometheus_fastapi_instrumentator import Instrumentator

class UserCreate(BaseModel):
    name: str

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_USER = "postgres"
DB_PASS = "postgres"
DB_NAME = "fastapi_db"

# Connect to the postgres
def get_conn():
    for _ in range(10):
        try:
            return psycopg2.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASS,
                dbname=DB_NAME
            )
        except psycopg2.OperationalError:
            time.sleep(2)
    raise Exception("DB not ready")

# Connect to the DB and create the table on the App startup
@app.on_event("startup")
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Get users from the DB
@app.get("/users")
def get_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users;")  
    rows = cur.fetchall()                        
    cur.close()
    conn.close()
    users = [{"id": r[0], "name": r[1]} for r in rows]
    return users


# Add users to the DB
@app.post("/users")
def add_user(user: UserCreate):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name) VALUES (%s) RETURNING id;",(user.name,))
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"id": user_id, "name": user.name}


# Liveness probe (is app alive?)
@app.get("/health")
def health():
    return {"status": "ok"}

# Readiness probe (can app serve traffic?)
@app.get("/ready")
def ready():
    try:
        conn = get_conn()
        conn.close()
        return {"status": "ready"}
    except Exception:
        return {"status": "not ready"}

@app.get("/", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

Instrumentator().instrument(app).expose(app)

