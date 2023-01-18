import smtplib, ssl
from sqlite3 import DatabaseError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import datetime, time
from datetime import datetime, timedelta
from collections import Counter
import gspread
import base64
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from datetime import date
import json


with open('../../Json/keys.json') as f:
    config = json.load(f)

company_email = config['company_email']
# emailUsed = config['jane_email']
emailUsed = config['test_email']
test_email = config['test_email']
sheets_key = config['sheets_key']
staff_name = config['staff_name']
staff_email = config['staff_name']
staff_mobile = config['staff_mobile']
localpath = config['localpath']
company_email_password = config['company_email_password']
commission_rates = config['commission_rates']
supplier_agent_name = config['supplier_agent_name']
bank_account_name = config['bank_account_name']
bank_bsb = config['bank_bsb']
bank_account_number = config['bank_account_number']

class Email:
    def __init__(self):
        
        SERVICE_ACCOUNT_FILE = "../../Json/keys.json"
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        self.credentials = None
        self.credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.clients_list_sheet = sheets_key
        service = build("sheets", "v4", credentials=self.credentials)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.clients_list_sheet, range="Payment Plan").execute()
        values = result.get('values', [])
        self.database = pd.DataFrame(values)
        self.database.columns = ["First Name", "Last Name", "Due Date", "Amount Due", "Payment Number", "School", "Status", "Student Email", "Estimated Commission", "Test"]

    def update_sheet(self, database):
        gc = gspread.authorize(self.credentials)
        gs = gc.open_by_key(self.clients_list_sheet)
        payment_plan_worksheet = gs.worksheet('Payment Plan')
        set_with_dataframe(worksheet=payment_plan_worksheet, dataframe=database, include_index=False,
        include_column_header=False, resize=True)

    def get_data_to_list(self, column):
        list = self.database[column].tolist()
        return list

    def get_column(self, column):
        column = self.database[column]
        return column

    def get_payment_count(self, first_name, due_date_list):
        payment_count = 0
        for y in range(1, len(due_date_list)):
            if first_name == self.database.iloc[y]["First Name"] and self.database.iloc[y]["Status"] != "":
                payment_count +=1
                print(payment_count, "is payment count of ", first_name)
        return payment_count + 1

    def totalPaymentCounter(self, firstNameColumn):
        
        counter = 1
        for x in range(1, len(firstNameColumn)):
            if x == 1:
                self.database.at[x,"Payment Number"] = counter

            elif firstNameColumn[x] == firstNameColumn[x-1]:
                counter = counter + 1
                self.database.at[x,"Payment Number"] = counter

            elif firstNameColumn[x] != firstNameColumn[x-1]:
                counter = 1
                self.database.at[x,"Payment Number"] = counter

                
    def send_payment_email_agent(self, first_name, last_name, due_date_payment, due_amount, student_email, payment_count, name_count, school, x):
        
        # Initialise email creation
        email_message = MIMEMultipart("mixed")
        email_message['From'] = company_email
        email_message['To'] = emailUsed
        email_message['Subject'] = first_name + " " + last_name + " | Payment Plan - " + str(due_date_payment) + " - " + str(payment_count - 1) + " of " + str(name_count[self.database.iloc[x]["First Name"]])

        with open('../../Json/Logo.jpg', 'rb') as f:
            img_data = f.read()
        msgImage = MIMEImage(img_data)
        msgImage.add_header('Content-ID', '<msgImage>')

        email_message.attach(msgImage)

        html = '''
        <html>
            <body>
            <p>Dear Jane,</p>
            <p></p>
            <p>Hope you are well.</p>
            <p>Please see attached payment of the student. Details are as follows:</p>
            Student Name: {first_name} {last_name}
            <br>School: {school}
            <br>Due Date: {due_date_payment}
            <br>Amount:  <b><ins>{due_amount}</b></ins>
            <br>Payment No: {payment_count} of {total_payment_count} 
            <br>
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
            staff_name = staff_name,
            staff_email = staff_email,
            staff_mobile = staff_mobile,
            first_name = first_name,
            last_name = last_name,
            school = school,
            due_date_payment = due_date_payment,
            due_amount = due_amount,
            payment_count = payment_count - 1,
            total_payment_count = name_count[self.database.iloc[x]["First Name"]], 
        )

        # Attach the Payment Receipt Image from the Student's Folder
        email = email_message.attach(MIMEText(html, "html"))
        filenames = first_name + " " + last_name + " Payment " + str(payment_count - 1) + " of " + str(name_count[self.database.iloc[x]["First Name"]]) + ".jpg"
        attachmentPath = localpath + first_name + " " + last_name + "/Payments/" + filenames

        try:
            with open(attachmentPath, "rb") as attachment:
                p = MIMEApplication(attachment. read(),_subtype="pdf")
                p.add_header('Content-Disposition', 'attachment', filename= filenames)
            email_message.attach(p)
        except Exception as e:
            raise

        # Convert it as a string
        msg_full = email_message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(company_email, company_email_password)
            server.sendmail(company_email, emailUsed, msg_full)

    def send_direct_payment_email_agent(self, first_name, last_name, due_date_payment, due_amount, student_email, payment_count, name_count, school, x):
        
        # Initialise email creation
        email_message = MIMEMultipart("mixed")
        email_message['From'] = company_email
        email_message['To'] = emailUsed
        email_message['Subject'] = first_name + " " + last_name + " | Direct to School Payment | Payment Plan - " + str(due_date_payment) + " - " + str(payment_count - 1) + " of " + str(name_count[self.database.iloc[x]["First Name"]])
        
        #Read image and attach to email
        with open('../../Json/Logo.jpg', 'rb') as f:
            img_data = f.read()
        msgImage = MIMEImage(img_data)
        msgImage.add_header('Content-ID', '<msgImage>')
        email_message.attach(msgImage)

        #Email HTML Body
        html = '''
        <html>
            <body>
            <p>Dear Jane,</p>
            <p></p>
            <p>Hope you are well.</p>
            <p>Please see attached direct payment of the student. Details are as follows:</p>
            Student Name: {first_name} {last_name}
            <br>School: {school}
            <br>Due Date: {due_date_payment}
            <br>Amount:  <b><ins>{due_amount}</b></ins>
            <br>Payment No: {payment_count} of {total_payment_count} 
            <br>
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
            staff_name = staff_name,
            staff_email = staff_email,
            staff_mobile = staff_mobile,
            first_name = first_name,
            last_name = last_name,
            school = school,
            due_date_payment = due_date_payment,
            due_amount = due_amount,
            payment_count = payment_count - 1,
            total_payment_count = name_count[self.database.iloc[x]["First Name"]], 
        )

        # Attach the Payment Receipt Image from the Student's Folder
        email = email_message.attach(MIMEText(html, "html"))
        filenames = first_name + " " + last_name + " Payment " + str(payment_count - 1) + " of " + str(name_count[self.database.iloc[x]["First Name"]]) + ".jpg"

        try:
            with open(attachmentPath, "rb") as attachment:
                p = MIMEApplication(attachment. read(),_subtype="pdf")
                p.add_header('Content-Disposition', 'attachment', filename= filenames)
            email_message.attach(p)
        except Exception as e:
            raise

        # Convert it as a string
        msg_full = email_message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(company_email, company_email_password)
            server.sendmail(company_email, emailUsed, msg_full)

    def send_email_to_student(self, first_name, due_date_payment, due_amount, student_email, payment_count, name_count, x, due_date_list):
    
    # Generate today's date to be included in the email Subject
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
            <br>Reference: Payment Plan 
            <br>
            <br>Kindly send a screenshot of the payment proof by replying to this email. 
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
            print(student_email)
            server.sendmail(company_email, student_email, email_string)
            # server.sendmail(company_email, test_email, email_string)
    
def commission_calculator():


    data = Email()
    due_date_list = data.get_data_to_list("Due Date")
        # Add more vendors and rates as needed
    
    for x in range(1, len(due_date_list)):
        school = data.database.iloc[x]["School"]
        payment = data.database.iloc[x]["Amount Due"]   
        commission =  float(payment) * float(commission_rates.get(school, 0))
        data.database.at[x,"Test"] = commission

    data.update_sheet(data.database)


def main():
    data = Email()
    due_date_list = data.get_data_to_list("Due Date")
    student_email_list = data.get_data_to_list("Student Email")
    first_name_list = data.get_data_to_list("First Name")
    due_amount = data.get_column("Amount Due")
    
    name_list = data.database.iloc[:,0]
    name_count = Counter(name_list)

    today = date.today()
    current_date = today.strftime("%d/%m/%Y")
    current_date = datetime.strptime(current_date, '%d/%m/%Y').date()



    for x in range(1, len(due_date_list)):

        first_name = data.database.iloc[x]["First Name"]
        last_name = data.database.iloc[x]["Last Name"]
        school = data.database.iloc[x]["School"]
        current_status = data.database.iloc[x]["Status"]
        student_email = student_email_list[x]
        due_date = due_date_list[x]
        due_amount = data.database.iloc[x]["Amount Due"]
        due_date_payment = datetime.strptime(due_date_list[x], '%d/%m/%Y').date()
        due_date_less_7_days = due_date_payment - timedelta(days=8)
        current_date_plus_7_days = current_date + timedelta(days=8)

        print(due_date_payment, "is the payment date")
        if current_status == "Paid":
            payment_count = data.get_payment_count(first_name, due_date_list)
            data.send_payment_email_agent(first_name, last_name, due_date_payment, due_amount, student_email, payment_count, name_count, school, x)
            data.database.at[x,"Status"] = "Sent to" + supplier_agent_name
        
        elif current_status == "Direct Payment":
            payment_count = data.get_payment_count(first_name, due_date_list)
            data.send_direct_payment_email_agent(first_name, last_name, due_date_payment, due_amount, student_email, payment_count, name_count, school, x)
            data.database.at[x,"Status"] = "Sent to " + supplier_agent_name + " - Direct Payment"
        
        elif current_status == "Followed Up":
            break
        
        # elif current_date_plus_7_days > due_date_payment: # if Due Date is in the next 7 days
        elif current_date > due_date_less_7_days: # if Due Date is in the next 7 days
            if data.database.iloc[x]["Status"] == "": # if Status
                # print(first_name,  ": ", due_date_payment)
                payment_count = data.get_payment_count(first_name, due_date_list)
                data.send_email_to_student(first_name, due_date_payment, due_amount, student_email, payment_count, name_count, x, due_date_list)
                data.database.at[x,"Status"] = "Followed up"
        else:
            break
    #Update the Google Sheet after everything is checked


    data.update_sheet(data.database)

if __name__ == "__main__":
    main()

# commission_calculator() # uncomment if need to calculate commission
# data.totalPaymentCounter(first_name_list) # uncomment if need to count
