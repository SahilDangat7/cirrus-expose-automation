import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive"]
PARENT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

def get_drive_service():
    creds = None
    if Path("token.json").exists():
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("drive", "v3", credentials=creds)

def create_folder(service, name, parent_id=None):
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        meta["parents"] = [parent_id]
    folder = service.files().create(body=meta, fields="id").execute()
    return folder["id"]

def make_public(service, file_id):
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"}
    ).execute()

def upload_file(service, file_path, parent_id, mimetype="application/octet-stream"):
    media = MediaFileUpload(file_path, mimetype=mimetype)
    file = service.files().create(
        body={"name": Path(file_path).name, "parents": [parent_id]},
        media_body=media,
        fields="id"
    ).execute()
    return file["id"]

def upload_to_drive():
    service = get_drive_service()

    # ── Create main folder ─────────────────────────────────────────────
    folder_name = "Cirrus_Bernau_OranienburgerStr6"
    folder_id = create_folder(service, folder_name, parent_id=PARENT_FOLDER_ID)
    make_public(service, folder_id)
    print(f"✓ Created folder: {folder_name}")
    print(f"✓ Folder URL: https://drive.google.com/drive/folders/{folder_id}")

    # ── Upload filled Excel ────────────────────────────────────────────
    excel_path = "output/filled_template.xlsx"
    if Path(excel_path).exists():
        upload_file(service, excel_path, folder_id,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        print(f"✓ Uploaded Excel")

    # ── Create images subfolder ────────────────────────────────────────
    img_folder_id = create_folder(service, "images", parent_id=folder_id)
    make_public(service, img_folder_id)
    print(f"✓ Created images subfolder")

    # ── Upload all images ──────────────────────────────────────────────
    images_dir = Path("output/images")
    if images_dir.exists():
        image_files = list(images_dir.glob("*"))
        for img_path in image_files:
            if img_path.is_file():
                mime = "image/jpeg" if img_path.suffix.lower() in [".jpg", ".jpeg"] else "image/png"
                upload_file(service, str(img_path), img_folder_id, mimetype=mime)
        print(f"✓ Uploaded {len(image_files)} images")

    # ── Save links ─────────────────────────────────────────────────────
    links = {
        "folder_url": f"https://drive.google.com/drive/folders/{folder_id}",
        "images_url": f"https://drive.google.com/drive/folders/{img_folder_id}"
    }
    with open("output/drive_links.json", "w") as f:
        json.dump(links, f, indent=2)

    print(f"\n✓ Drive folder : {links['folder_url']}")
    print(f"✓ Images folder: {links['images_url']}")

if __name__ == "__main__":
    upload_to_drive()