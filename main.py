import os
import time
import json as JSON
import requests
import pyotp
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By

EMAILS_FILE = "emails.json"
SENT_EMAILS_FILE = "sent_emails.json"

def get_emails(totp_secret, username, password):
    # Generate TOTP token
    totp = pyotp.TOTP(str(totp_secret))
    totp_token = totp.now()

    print("TOTP Token:", totp_token)

    # Set up Firefox options for headless mode
    options = FirefoxOptions()
    options.add_argument("--headless")

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    try:
        # Open the login page
        driver.get("https://owa.h-ka.de/owa/auth/logon.aspx")

        # Find and fill the username field
        username_field = driver.find_element(By.NAME, "username")
        username_field.send_keys(str(username))

        # Find and fill the password field
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(totp_token)  # Use the TOTP token as the password

        # Submit the form
        password_field.submit()

        # Wait for the page to load
        time.sleep(5)  # Adjust the sleep time as needed

        username_field = driver.find_element(By.NAME, "username")
        username_field.send_keys(str(username))

        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(str(password))

        password_field.submit()

        time.sleep(5)

        # Locate the email list container
        email_list = driver.find_elements(By.CSS_SELECTOR, "div._lvv_w")

        emails = []
        # Extract details of the first 10 emails
        for email in email_list[:10]:
            sender = email.find_element(By.CSS_SELECTOR, "span.lvHighlightFromClass").text
            subject = email.find_element(By.CSS_SELECTOR, "span.lvHighlightSubjectClass").text
            time_received = email.find_element(By.CSS_SELECTOR, "span._lvv_M").text
            content = email.find_element(By.CSS_SELECTOR, "span.ms-font-weight-semilight").text
            print(f"Sender: {sender}, Subject: {subject}, Time: {time_received}, Content: {content}")
            emails.append({
                "sender": sender,
                "subject": subject,
                "time_received": time_received,
                "content": content
            })
        # Save Emails to JSON
        with open(EMAILS_FILE, "w") as f:
            f.write(JSON.dumps(emails))
    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()

def load_sent_emails():
    if os.path.exists(SENT_EMAILS_FILE):
        with open(SENT_EMAILS_FILE, "r") as f:
            return JSON.load(f)
    return []

def save_sent_emails(emails):
    with open(SENT_EMAILS_FILE, "w") as f:
        f.write(JSON.dumps(emails))

def send_update():
    try:
        # Load webhook URL from environment variables
        webhook_url = os.getenv('WEBHOOK_URL')
        if not webhook_url:
            print("Please set the WEBHOOK_URL environment variable.")
            return

        # Read emails from file
        with open(EMAILS_FILE, "r") as f:
            emails = JSON.load(f)

        # Load previously sent emails
        sent_emails = load_sent_emails()

        # Identify new emails
        new_emails = [email for email in emails if email not in sent_emails]

        # Format the message for Discord
        messages = []
        for email in new_emails:
            message = f"**Sender:** {email['sender']}\n**Subject:** {email['subject']}\n**Time Received:** {email['time_received']}\n**Content:** {email['content']}"
            messages.append({"content": message})

        # Send new emails to webhook
        for message in messages:
            response = requests.post(webhook_url, json=message)
            if response.status_code == 204:
                print("Email sent successfully.")
            else:
                print(f"Failed to send email. Status Code: {response.status_code}")

        # Update sent emails
        save_sent_emails(emails)
    except Exception as e:
        print("An error occurred while sending the update:", e)

def main():
    print("Starting the OWA email scraper...")
    # Load secrets from environment variables
    username = os.getenv('OWA_USERNAME')
    password = os.getenv('OWA_PASSWORD')
    totp_secret = os.getenv('TOTP_SECRET')

    if not username or not password or not totp_secret:
        print("Please set the OWA_USERNAME, OWA_PASSWORD, and TOTP_SECRET environment variables.")
        exit(1)
    while True:
        get_emails(totp_secret, username, password)
        send_update()
        time.sleep(300)

if __name__ == "__main__":
    main()
