import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv
import logging
import schedule
import time
import gspread

from oauth2client.service_account import ServiceAccountCredentials


# Load email credentials
load_dotenv()
EMAIL_ADDRESS = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')


VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Setup Logging
LOG_FILE = "email_log.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

#Birthday Email Sender Function
def send_birthday_emails(students):
    today = datetime.today().strftime('%m-%d')
    logging.info("🎬 Running birthday email check...")

    for student in students:
        try:
            birthdate = datetime.strptime(student['birthdate'], '%Y-%m-%d').strftime('%m-%d')
            print(birthdate)
        except Exception as e:
            logging.info(f"⚠️ Invalid birthdate format for {student}: {e}")
            continue

        if birthdate == today:
            msg = EmailMessage()
            msg['Subject'] = f"🎉 Happy Birthday!"
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = student['email']

            # Plain text fallback
            msg.set_content(f"Hi {student['name']},\n\nWishing you a fantastic birthday!")
            # HTML version
            msg.add_alternative(f"""
    <html>
  <body style="margin:0; padding:0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color:#f4f4f4;">
    <table width="100%" bgcolor="#f4f4f4" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td align="center" style="padding: 20px 10px;">
          <table width="600" bgcolor="#ffffff" cellpadding="0" cellspacing="0" border="0" style="border-radius: 10px; box-shadow: 0 6px 15px rgba(0,0,0,0.08); overflow: hidden;">
            
            <!-- Logo -->
            <tr>
              <td align="center" style="background-color:#ffffff; padding: 40px 20px 20px 20px;">
                <img src="https://i.ibb.co/G3xBbGvG/image.png" alt="Stanford Logo" width="220" style="display: block; max-width: 100%; height: auto;" />
              </td>
            </tr>

            <!-- Yellow Divider -->
            <tr>
              <td style="background-color: #ffc600; height: 4px;"></td>
            </tr>

            <!-- Birthday Message -->
            <tr>
              <td style="padding: 50px 50px 0 50px; color: #333333; font-size: 17px; line-height: 1.7; text-align: center;">
                <h2 style="margin: 0; font-size: 28px; color: #222;">🎉 Happy Birthday {student['name']} !! 🎉</h2>
                <p style="margin: 12px 0 0 0; font-size: 16px; color: #666;">
                  We're glad to be part of your journey in Australia. 
                </p>
              </td>
            </tr>

            <!-- Message Body -->
            <tr>
              <td style="padding: 30px 50px 30px 50px; color: #333333; font-size: 17px; line-height: 1.7; text-align: center;">
                <p style="margin-top: 0;">
                  May your day be filled with love, laughter, and everything that brings you joy. 
                  Wishing you continued success and happiness in the year ahead.
                </p>
                <p style="margin-top: 40px; font-style: italic; color: #666;">
                  With warm wishes,<br />
                  The Stanford International Team
                </p>
              </td>
            </tr>
            
            <!-- PR Pathway Short Note -->
            <tr>
              <td style="padding: 0 50px 30px 50px; color: #333; font-size: 15px; line-height: 1.6; text-align: center;">
                <p style="margin: 0;">
                  🎓 Chasing your Down Under dream? <br/>
                  <span style="font-style:italic">Find out how your studies can open doors to exciting future opportunities in Australia.</span>
                </p>
              </td>
            </tr>


            <!-- Footer -->
            <tr>
              <td bgcolor="#eaeaea" style="padding: 25px 50px 20px 50px; font-size: 14px; color: #000000; text-align: center;">
                <p style="margin: 0 0 10px 0; font-weight: bold;">
                  Get in touch
                </p>
                <p style="margin: 5px 0;">
                  <span style="display: inline-flex; align-items: center; gap: 6px;">
                    <img src="https://cdn-icons-png.flaticon.com/16/724/724664.png" alt="Call Icon" width="16" height="16" style="vertical-align: middle;" />
                    <a href="tel:0413502523" style="color: #000000; text-decoration:none;">  0413 502 523</a>
                  </span><br/>
                  <a href="mailto:studentsupport@stanfordinternational.com.au" style="color: #000000; text-decoration:none;">studentsupport@stanfordinternational.com.au</a>
                </p>
                <p style="margin: 15px 0 0 0;">
                  <!-- Social icons -->
                  <a href="https://www.facebook.com/people/Stanford-International/100091273596220/?mibextid=LQQJ4d" style="margin: 0 8px; text-decoration:none;">
                    <img src="https://cdn-icons-png.flaticon.com/24/733/733547.png" alt="Facebook" width="24" height="24" />
                  </a>
                  <a href="https://www.linkedin.com/company/stanford-international/" style="margin: 0 8px; text-decoration:none;">
                    <img src="https://cdn-icons-png.flaticon.com/24/733/733561.png" alt="LinkedIn" width="24" height="24" />
                  </a>
                  <a href="https://www.instagram.com/stanfordinternational_" style="margin: 0 8px; text-decoration:none;">
                    <img src="https://cdn-icons-png.flaticon.com/24/733/733558.png" alt="Instagram" width="24" height="24" />
                  </a>
                  <a href="https://wa.me/61413502523" style="margin: 0 8px; text-decoration:none;">
                    <img src="https://cdn-icons-png.flaticon.com/24/733/733585.png" alt="WhatsApp" width="24" height="24" />
                  </a>
                </p>
              </td>
            </tr>

            <!-- Copyright -->
            <tr>
              <td bgcolor="#ffc600" style="color: #000000; font-size: 12px; text-align: center; padding: 12px 20px; font-weight: 500;">
                © Stanford International. All rights reserved.
              </td>
            </tr>

          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
""", subtype='html')

            try:
                with smtplib.SMTP('smtp.office365.com', 587) as smtp:
                    smtp.starttls()  # Secure the connection
                    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    smtp.send_message(msg)
                    print('message send')
                logging.info(f"✅ Email sent to {student['name']} at {student['email']}")
                print('email sent')
            except Exception as e:
                print(e)
                logging.error(f"❌ Failed to send email to {student['email']}: {e}")
        else:
            logging.debug(f"📅 Not {student['name']}'s birthday today.")


def get_students_from_sheet():
    students = []
    records = sheet.get_all_records()
    
    today = datetime.today()
    today_str = today.strftime("%m-%d")

    for row in records:
        # Normalize keys
        row = {k.strip().lower(): v for k, v in row.items()} 

        birthdate = row.get("birthdate")
        if row.get("name") and row.get("email") and birthdate:
            try:
                bd_date = datetime.strptime(birthdate.strip(), "%Y-%m-%d")
            except ValueError:
                logging.info(f"Skipping row due to invalid birthdate format: {birthdate}")
                continue

            if bd_date.strftime("%m-%d") == today_str:
                students.append({
                    "name": row["name"].strip(),
                    "email": row["email"].strip(),
                    "birthdate": birthdate.strip()
                })
                logging.info(f"Added student: {row['name'].strip()} with birthday today")
        else:
            logging.info(f"Skipping row due to missing data: {row}")

    logging.info(f"Total students with birthday today: {len(students)}")
    print(students)
    return students



schedule.every().day.at("16:11").do(lambda: send_birthday_emails(get_students_from_sheet()))
print("Scheduler Running")

logging.info("📬 Birthday email scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(60)