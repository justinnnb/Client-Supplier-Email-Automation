from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from werkzeug.utils import secure_filename
import json
from datetime import datetime, timedelta, date
from .token_utils import generate_token, verify_token

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}},always_send=False)  # Enable CORS for all routes and origin 'http://localhost:5173'



# Load configuration from environment variables or a JSON file
# with open('keys.json') as f:
#     config = json.load(f)

# company_email = config['company_email']
# company_email_password = config['company_email_password']
# sheets_key = config['sheets_key']
# localpath = config['localpath']

# SERVICE_ACCOUNT_FILE = 'path/to/credentials.json'
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
# credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# drive_service = build('drive', 'v3', credentials=credentials)

@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()
    
@app.route('/api/upload_payment', methods=['POST'])
def upload_payment():
    
    # Extract token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header missing or invalid"}), 401

    token = auth_header.split(' ')[1]

    # Verify token
    token_data = verify_token(token)
    if not token_data:
        print('token fail')
        return jsonify({"error": "Invalid token"}), 401

    # Get the file from the request
    print('check file')
    if 'file' not in request.files:
        print('no file')
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    print(token_data, 'file success')

    # Get additional data from the request form
    first_name = token_data['data']['first_name']
    last_name = token_data['data']['last_name']
    due_date = token_data['data']['due_date']
    amount_due = token_data['data']['amount_due']
    student_email = token_data['data']['student_email']

    return jsonify({"file_id": file_drive.get('id')}), 200


@app.route('/verify_token', methods=['POST'])
def verify_token_route():
    token = request.json.get('token')
    if not token:
        return jsonify({"error": "Token is missing"}), 400
    
    data = verify_token(token)
    if data is None:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    return jsonify({"data": data}), 200



if __name__ == '__main__':
    app.run(debug=True, port=5010)
