import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ==========================
# 📧 Email Function
# ==========================
def send_email(subject, body):
    sender_email = os.getenv("EMAIL_USER")  # GitHub Secret
    receiver_email = os.getenv("EMAIL_USER")  # ممكن تخليها بريد مختلف
    password = os.getenv("EMAIL_PASS")       # GitHub Secret

    if not sender_email or not password:
        print("❌ Email credentials not found. Please set EMAIL_USER and EMAIL_PASS as secrets.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent: {subject}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


# ==========================
# 🔍 Check Updates Function
# ==========================
def check_for_updates(url, keyword):
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)

    try:
        # البحث عن زر الاشتراك
        subscribe_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".b-offer-join__btn, .m-rounded.m-flex.m-space-between.m-lg.g-btn")
            )
        )
        print(f"🔎 Found subscribe button on {url}")

        button_text = subscribe_button.text.lower()
        if keyword.lower() in button_text:
            send_email(f"Update Found on {url}", f"There's a free offer available on {url}")
            driver.quit()
            return True
        else:
            driver.quit()
            return False
    except Exception as e:
        print(f"⚠️ Failed to check {url}: {str(e)}")
        driver.quit()
        return False


# ==========================
# 📂 Load URLs from file
# ==========================
def load_urls_from_file(filename):
    with open(filename, 'r') as file:
        urls = file.readlines()
    return [url.strip() for url in urls]


# ==========================
# 🚀 Main Execution
# ==========================
if __name__ == "__main__":
    urls = load_urls_from_file('urls.txt')  # لازم يبقى موجود في نفس المجلد
    keyword = "free for"

    for url in urls:
        print(f"➡️ Checking {url}...")
        check_for_updates(url, keyword)

    print("✅ Finished checking all URLs.")
