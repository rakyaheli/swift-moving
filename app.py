from flask import Flask, render_template, request, redirect, url_for
from database import init_db, get_db, save_quote_request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.config['DATABASE'] = 'swift_moving.db'

# ------------------ Email Configuration ------------------
EMAIL_ADDRESS = "swiftmoving.il@gmail.com"
EMAIL_PASSWORD = "veimwvdqufovzzmd"  # Gmail App Password
EMAIL_RECIPIENT = "swiftmoving.il@gmail.com"

# ------------------ Initialize Database ------------------
init_db(app)

# ------------------ Routes ------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone', '')
        message = request.form['message']

        send_contact_email(name, email, phone, message)
        return redirect(url_for('confirmation'))

    return render_template('contact.html')

@app.route('/quote', methods=['GET', 'POST'])
def quote():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        move_date = request.form['move_date']
        service_type = request.form['service_type']
        origin = request.form['origin']
        destination = request.form['destination']
        message = request.form['message']
        
        # Save to database
        save_quote_request(name, email, phone, move_date, service_type, origin, destination, message)

        # Send email to business and confirmation to user
        send_quote_email(name, email, phone, move_date, service_type, origin, destination, message)
        return redirect(url_for('confirmation'))

    return render_template('quote.html')

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

# ------------------ Email Sending Functions ------------------

def send_contact_email(name, email, phone, message):
    subject = "New Contact Form Submission - Swift Moving"
    body = f"""
    You have a new contact form submission:

    Name: {name}
    Email: {email}
    Phone: {phone}

    Message:
    {message}
    """

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Contact email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send contact email: {e}")

def send_quote_email(name, user_email, phone, move_date, service_type, origin, destination, message):
    # Email to business
    subject_owner = f"New Quote Request from {name}"
    body_owner = f"""
    New Quote Request:

    Name: {name}
    Email: {user_email}
    Phone: {phone}
    Move Date: {move_date}
    Service Type: {service_type}
    Origin: {origin}
    Destination: {destination}
    Message: {message}
    """

    msg_owner = MIMEMultipart()
    msg_owner['From'] = EMAIL_ADDRESS
    msg_owner['To'] = EMAIL_RECIPIENT
    msg_owner['Subject'] = subject_owner
    msg_owner.attach(MIMEText(body_owner, 'plain'))

    # Confirmation email to user
    subject_user = "Your Quote Request to Swift Moving"
    body_user = f"""
    Hi {name},

    Thank you for contacting Swift Moving! We’ve received your quote request.

    📦 Your Details:
    • Move Date: {move_date}
    • Service Type: {service_type}
    • From: {origin}
    • To: {destination}
    • Message: {message}

    We’ll contact you soon!

    — Swift Moving Team
    """

    msg_user = MIMEMultipart()
    msg_user['From'] = EMAIL_ADDRESS
    msg_user['To'] = user_email
    msg_user['Subject'] = subject_user
    msg_user.attach(MIMEText(body_user, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg_owner)
            smtp.send_message(msg_user)
        print("✅ Quote email sent to business and confirmation sent to user.")
    except Exception as e:
        print(f"❌ Failed to send quote email: {e}")

# ------------------ Run App ------------------
if __name__ == '__main__':
    app.run(debug=True)
