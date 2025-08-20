import requests
from io import BytesIO
import os

def hello():
    print("Hello from Tapestry!")


def fetch_library_data(token, folder_details):
    folder_name = folder_details.get("name")
    tapestry_id = folder_details.get("tapestry_id")

    url =  "https://inthepicture.org/admin/library"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "limit": 10,
        "page": 1,
        "active": "grid",
        "group_id": [],
        "tapestry_id": tapestry_id,
        "parent": folder_name,
    }
    
    response = requests.post(url, headers=headers, json=data)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }

def image_to_text(token, user_prompt, document, name ,system_prompt=""):

    url =  "https://inthepicture.org/admin/image_to_text"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "user_prompt": user_prompt,
        "document": document,
        "sytem_prompt": system_prompt,
        "name": name
    }
    
    response = requests.post(url, headers=headers, json=data)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }

def fetch_group_data(token, group_ids,tapestry_id, name):

    url =  "https://inthepicture.org/admin/fetch_group_data"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "group_ids": group_ids,
        "tapestry_id": tapestry_id,
        "name" : name
    }
    
    response = requests.post(url, headers=headers, json=data)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }

def selected_document_data(token, document_ids,tapestry_id,name):

    url =  "https://inthepicture.org/admin/selected_document_data"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "document_ids": document_ids,
        "tapestry_id": tapestry_id,
        "name": name
    }
    
    response = requests.post(url, headers=headers, json=data)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }

def fetch_ai_chat(token, tapestry_id, tapestry_user_id, session_id, name):
    url =  "https://inthepicture.org/admin/fetch_ai_chat"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "tapestry_id": tapestry_id,
        "tapestry_user_id": tapestry_user_id,
        "name": name
    }
    if session_id:
        data["session_id"] = session_id
    response = requests.post(url, headers=headers, json=data)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }

def fetch_sticky_notes(token, tapestry_id, tapestry_user_id, name):
    url =  "https://inthepicture.org/admin/fetch_sticky_notes"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "tapestry_id": tapestry_id,
        "tapestry_user_id": tapestry_user_id,
        "name": name
    }
    response = requests.post(url, headers=headers, json=data)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }

def fetch_documents(token, tapestry_id, tapestry_user_id, group_ids, name):
    url =  "https://inthepicture.org/admin/fetch_documents"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "tapestry_id": tapestry_id,
        "tapestry_user_id": tapestry_user_id,
        "name": name
    }
    print("Request body:", data)

    if group_ids and len(group_ids) > 0:
        data["group_ids"] = group_ids
    
    response = requests.post(url, headers=headers, json=data)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }

def ask_ai_question(token, question, tapestry_id, session_id=None, group_ids=None, document_name=None,ai_type=None):
    url = "https://inthepicture.org/admin/ask_ai_question"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    
    data = {
        "question": question,
        "tapestry_id": tapestry_id
    }

    # Optional fields
    if session_id is not None:
        data["session_id"] = session_id
    if group_ids:
        data["group_ids"] = group_ids
    if document_name:
        data["documentName"] = document_name
    if ai_type:
        data["type"] = ai_type

    response = requests.post(url, headers=headers, json=data)

    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }

def search_group(token, tapestry_id, search=None):
    url = "https://inthepicture.org/admin/search_group"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    data = {
        "tapestry_id": tapestry_id
    }

    if search:
        data["search"] = search

    print("Request body:", data)

    response = requests.post(url, headers=headers, json=data)

    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }

def change_tapestry_details(token, tapestry_id, parameters, name):
    url =  "https://inthepicture.org/admin/change_tapestry_details"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "tapestry_id": tapestry_id,
        "parameters": parameters,
        "name": name
    }
    
    response = requests.post(url, headers=headers, json=data)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }
    
def set_load_Status(token, session_id):
    url =  "https://inthepicture.org/admin/set_load_Status"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "session_id": session_id,
    }
    
    response = requests.post(url, headers=headers, json=data)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }
    
def upload_file(token, tapestry_id, file_url, file_title, description, caption):
    url =  "https://inthepicture.org/admin/uplaod_file"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "tapestry_id": tapestry_id,
        "file_url": file_url,
        "file_title": file_title,
        "description": description,
        "caption": caption,
    }
    
    response = requests.post(url, headers=headers, json=data)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }

def upload_to_s3(token, tapestry_id, blob, app_name, doc_name,  content_type=None ):
    url = "https://inthepicture.org/admin/uplaod_to_s3"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
    }

    # Determine if blob is a file path or raw content
    if isinstance(blob, str) and os.path.isfile(blob):
        file_like = open(blob, "rb")
    else:
        if isinstance(blob, str):
            blob = blob.encode('utf-8')
        file_like = BytesIO(blob)

    # If no content_type provided, guess based on doc_name extension
    if not content_type:
        if doc_name.lower().endswith(".pdf"):
            content_type = "application/pdf"
        elif doc_name.lower().endswith(".txt"):
            content_type = "text/plain"
        elif doc_name.lower().endswith((".jpg", ".jpeg")):
            content_type = "image/jpeg"
        elif doc_name.lower().endswith(".png"):
            content_type = "image/png"
        else:
            content_type = "application/octet-stream"

    files = {
        "blob": (doc_name, file_like, content_type),
    }
    data = {
        "tapestry_id": tapestry_id,
        "app_name": app_name,
        "doc_name": doc_name,
    }
    response = requests.post(url, headers=headers, files=files, data=data)

    # Close file if it was opened from disk
    if isinstance(blob, str) and os.path.isfile(blob):
        file_like.close()

    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }
    
def list_s3_doc(token, tapestry_id):
    url =  "https://inthepicture.org/admin/list_s3_doc"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "tapestry_id": tapestry_id,
    }
    
    response = requests.post(url, headers=headers, json=data)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }
    
def update_s3_doc(token, doc_id, blob, content_type=None):
    url = "https://inthepicture.org/admin/update_s3_doc"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
    }

    # Determine if blob is a file path or raw content
    if isinstance(blob, str) and os.path.isfile(blob):
        file_like = open(blob, "rb")
    else:
        if isinstance(blob, str):
            blob = blob.encode('utf-8')
        file_like = BytesIO(blob)

    # Fallback: set content_type if not provided
    if not content_type:
        content_type = "application/octet-stream"

    files = {
        "blob": ("file", file_like, content_type),
    }
    data = {
        "doc_id": doc_id,
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    # Close file if opened from disk
    if isinstance(blob, str) and os.path.isfile(blob):
        file_like.close()

    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        return {
            "success": False,
            "code": response.status_code,
            "message": resp_json.get("message", response.text),
            "body": {}
        }

def delete_s3_doc(token, doc_id):
    url = "https://inthepicture.org/admin/delete_s3_doc"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
    }
    data = {
        "doc_id": doc_id,
    }

    response = requests.post(url, headers=headers, data=data)

    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }
