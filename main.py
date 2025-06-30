from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
import os
import re
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fastapi.responses import JSONResponse

load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

app = FastAPI(root_path="/api")


phone_pattern = re.compile(r'\b\d{7,}\b')
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
   
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return PlainTextResponse(content=params.get("hub.challenge"), status_code=200)
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def receive_message(request: Request):
    try:
        body = await request.body()
        if not body:
            print('body not found')
            return JSONResponse(content={"message": "Empty body"}, status_code=200)

        payload = json.loads(body)
        print("Received:", payload)
        

        for entry in payload.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                message_text = messaging_event.get("message", {}).get("text")

                if message_text:
                     # Get sender name from Facebook Graph API
                    user_info_url = f"https://graph.facebook.com/{sender_id}"
                    params = {
                        "fields": "first_name,last_name",
                        "access_token": PAGE_ACCESS_TOKEN
                    }
                    user_response = requests.get(user_info_url, params=params)
                    user_data = user_response.json()

                    first_name = user_data.get("first_name", "")
                    last_name = user_data.get("last_name", "")
                    print(first_name,last_name)
                    full_name = f"{first_name} {last_name}".strip()


                    print(f"Sender: {full_name} - Message: {message_text}")

                    phone_matches = phone_pattern.findall(message_text)
                    if phone_matches:
                        for raw_phone in phone_matches:
                            cleaned_phone = re.sub(r'\D', '', raw_phone)  # Remove non-digits
                            print(f"Saving: {full_name} - {cleaned_phone}")
                            sheet.append_row([full_name, cleaned_phone])
                    else:
                        print(f"No phone found in message: {message_text}")

                    # Now save to Google Sheet or wherever
        return JSONResponse(content={"status": "ok"}, status_code=200)

    except json.JSONDecodeError:
        print("Webhook received non-JSON or malformed JSON")
        return JSONResponse(content={"error": "Invalid JSON"}, status_code=200)