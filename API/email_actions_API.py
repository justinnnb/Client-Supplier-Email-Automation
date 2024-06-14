from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import pandas as pd
import time
import json
from datetime import datetime, timedelta, date

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load configuration from environment variables or a JSON file
with open('keys.json') as f:
    config = json.load(f)

company_email = config['company_email']
company_email_password = config['company_email_password']
sheets_key = config['sheets_key']
localpath = config['localpath']

SERVICE_ACCOUNT_FILE = 'path/to/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

@app.route('/api/send-email', methods=['POST'])
def send_email():
    data = request.json
    # Extract data from the request
    first_name = data['first_name']
    last_name = data['last_name']
    due_date_payment = data['due_date_payment']
    due_amount = data['due_amount']
    student_email = data['student_email']
    payment_count = data['payment_count']
    name_count = data['name_count']
    school = data['school']

    # Logic to send email (similar to your existing script)
    email_message = MIMEMultipart("mixed")
    email_message['From'] = company_email
    email_message['To'] = student_email
    email_message['Subject'] = f"{first_name} {last_name} | Payment Plan - {due_date_payment} - {payment_count}"

    html = '''
    <html>
        <body>
        <p>Dear {first_name},</p>
        <p>...</p>
        </body>
    </html>
    '''.format(first_name=first_name)

    email_message.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(company_email, company_email_password)
        server.sendmail(company_email, student_email, email_message.as_string())
    return jsonify({"message": "Email sent successfully"}), 200



@app.route('/upload_payment/<token>', methods=['POST'])
def upload_payment(token):

    file = request.files['file']
    student_name = request.form['student_name']
    folder_id = request.form['folder_id']
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(localpath, filename)
    file.save(filepath)

    # Upload to Google Drive
    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaFileUpload(filepath, mimetype='image/jpeg')
    file_drive = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    return jsonify({"file_id": file_drive.get('id')}), 200




if __name__ == '__main__':
    app.run(debug=True)
