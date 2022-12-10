import os

from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse
from bson.binary import Binary
from pymongo import MongoClient
from typing import List
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
user_names = []
user_files = {}
client = ""
DB_URL = os.environ.get("DB_URL")


def connect_to_db():
    try:
        global client
        # Create a MongoClient object
        client = MongoClient(DB_URL)
        # Connect to the database
        DB = client.filemanager
        # Get the collection
        collection = DB.files
        # cluster = \
        # MongoClient("mongodb+srv://notuser:notuser@filemanager.s1krore.mongodb.net/?retryWrites=true&w=majority")
        # db = cluster["filemanager"]
        # db = cluster.grid_file
        print("Connected to DB successfully")
        return collection
    except Exception as e:
        print(f"Error in mongo DB connecting {e}")


# TODO @implement home connection to submit files and get files
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/{username}", response_class=HTMLResponse)
def submit_files(request: Request, username: str):
    global user_names
    if username not in user_names:
        user_names.append(username)
        user_files[username] = []
    return templates.TemplateResponse(
        "submitFiles.html", {"request": request, "username": username}
    )


@app.post("/submitform", response_class=HTMLResponse)
async def handle_form(
    username: str = Form(...), newFiles: List[UploadFile] = File(...)
):
    collection = connect_to_db()
    global user_files
    current_user_files = user_files[username]
    print(username)
    for file in newFiles:
        current_user_files.append(file.filename)
        file_content = await file.read()
        print(file.filename)
        print(file_content)
        # Define the file info, path, and name
        file_info = {
            "name": file.filename,
            "path": file.filename,
            "size": 1024,
            "data": file_content,
        }
        collection.insert_one(file_info)
        # Print a success message
        print("File added successfully!")

    client.close()
    user_files[username] = current_user_files
    returnPage = open("templates/filesSubmitted.html", "r")
    returnPageContent = returnPage.read()
    return HTMLResponse(content=returnPageContent, status_code=200)


@app.get("/get-files/{user_name}", response_class=HTMLResponse)
def get_file(request: Request, user_name):
    collection = connect_to_db()
    if user_name not in user_names:
        return templates.TemplateResponse(
            "getFiles.html",
            {
                "request": request,
                "username": user_name,
                "results": "This user doesn't exist",
            },
        )
    global user_files
    files = []
    for file_name in user_files[user_name]:
        file = collection.find_one({"name": file_name})
        file_data = file["data"]
        files.append((file_name, file_data))
        print(f"file name: {file_name}")
        print(file_data)

    return templates.TemplateResponse(
        "getFiles.html", {"request": request, "username": user_name, "results": files}
    )


# if __name__ == '__main__':
