from flask import Flask, request, jsonify
from token_utils import generate_token, verify_token
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

app = Flask(__name__)

# Configure your Google Drive API
SERVICE_ACCOUNT_FILE = '../../Json/keys.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# Endpoint to send email (simplified for this example)
@app.route('/send_reminder', methods=['POST'])
def send_reminder():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    student_email = data.get('student_email')
    due_date_payment = data.get('due_date_payment')
    due_amount = data.get('due_amount')
    payment_count = data.get('payment_count')

    token_data = {'first_name': first_name, 'last_name': last_name, 'email': student_email}
    token = generate_token(token_data)
    upload_link = f"http://yourfrontend.com/upload?token={token}"

    # Code to send email goes here (use the provided send_email_to_student method logic)
    # ...
    email_message = MIMEMultipart()
    email_message['From'] = company_email
    # email_message['To'] = test_email
    email_message['To'] = student_email
    email_message['Subject'] = first_name + " - Tuition Fees due on " + str(due_date_payment) + " | Payment " + str(payment_count) + " of " + str(name_count[self.database.iloc[x]["First Name"]])

    # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
    with open('../../Json/Logo.jpg', 'rb') as f:
        img_data = f.read()
    msgImage = MIMEImage(img_data)
    msgImage.add_header('Content-ID', '<msgImage>')

    email_message.attach(msgImage)
    html = '''
    <html>
        <body>
        <p>Dear {first_name},</p>
        <p></p>
        <p>This is a courtesy reminder that your next tuition fee payment is due on <b><ins>{due_date_payment}</b></ins>.</p>
        <p>Kindly send payment to bank account below:</p>
        Account Name: {bank_account_name}
        <br>BSB: {bank_bsb}
        <br>Account Number: {bank_account_number}
        <br>Amount:  <b><ins>{due_amount}</b></ins>
        <br>Reference: {last_name} {first_name}
        <br>
        <br>Kindly send a screenshot of the payment proof by replying to this email. 
        <br> <b><ins>Don't forget to include your full name as the payment reference.</b></ins>
        <br>
        <br>Thank you very much.
        <br>
        <br><b>{staff_name}</b>
        <br>Travel and Study Consultant
        <br>E: {staff_email}
            <br>M: {staff_mobile}
            <br><img src="cid:msgImage" alt="Logo">

            <p></p>
            <p></p>
        </body>
    </html>
    '''.format(
        bank_account_name = bank_account_name,
        bank_bsb = bank_bsb,
        bank_account_number = bank_account_number,
        staff_name = staff_name,
        staff_email = staff_email,
        staff_mobile = staff_mobile,         
        first_name = first_name,
        last_name = last_name,
        due_date_payment = due_date_payment,
        due_amount = due_amount
    )

    email_message.attach(MIMEText(html, "html"))
    # Convert it as a string
    email_string = email_message.as_string()

    email_message.attach(MIMEText(html, 'html'))

    print(payment_count)

    # Connect to the Gmail SMTP server and Send Email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(company_email, company_email_password)
        if student_email == "":
            print(student_email)
            print(first_name, last_name, ' blank email. Please check.')
        else:
            print(student_email)
            server.sendmail(company_email, student_email, email_string)
        # server.sendmail(company_email, test_email, email_string)

    return jsonify({'message': 'Reminder sent', 'upload_link': upload_link}), 200

# Endpoint to handle file uploads
@app.route('/upload_receipt', methods=['POST'])
def upload_receipt():
    token = request.args.get('token')
    file = request.files.get('file')

    if not token or not file:
        return jsonify({'error': 'Token and file are required'}), 400

    user_data = verify_token(token)
    if not user_data:
        return jsonify({'error': 'Invalid or expired token'}), 401

    # Define the Google Drive folder structure and upload the file
    folder_name = f"{user_data['first_name']} {user_data['last_name']}"
    folder_id = get_or_create_folder(drive_service, folder_name)
    file_id = upload_to_drive(drive_service, file, folder_id)

    return jsonify({'message': 'File uploaded successfully', 'file_id': file_id}), 200

def get_or_create_folder(service, folder_name):
    # Check if the folder exists, if not create it
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    response = service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])

    if files:
        return files[0]['id']
    else:
        file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

def upload_to_drive(service, file, folder_id):
    file_metadata = {'name': file.filename, 'parents': [folder_id]}
    media = MediaFileUpload(file, mimetype=file.mimetype)
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return uploaded_file.get('id')

if __name__ == '__main__':
    app.run(debug=True)
