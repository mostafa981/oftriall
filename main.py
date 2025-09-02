from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


SENT_FILE = "sent_links.txt"


# ==========================
# 📂 Sent Links Handling
# ==========================
def load_sent_links():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r") as f:
        return set(line.strip() for line in f)


def save_sent_links(links):
    with open(SENT_FILE, "w") as f:
        for link in links:
            f.write(link + "\n")


# ==========================
# 📧 Email Function
# ==========================
def send_email(subject, body):
    sender_email = os.getenv("EMAIL_USER")
    receiver_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not sender_email or not password:
        print("❌ Missing EMAIL_USER or EMAIL_PASS secrets.")
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
def check_for_updates(url, keyword, sent_links):
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)

    try:
        subscribe_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".b-offer-join__btn, .m-rounded.m-flex.m-space-between.m-lg.g-btn")
            )
        )
        print(f"🔎 Found subscribe button on {url}")
        button_text = subscribe_button.text.lower()
        if keyword.lower() in button_text and url not in sent_links:
            send_email(f"Update Found on {url}", f"There's a free offer available on {url}")
            sent_links.add(url)
    except Exception as e:
        print(f"⚠️ Failed to check {url}: {e}")
    finally:
        driver.quit()


# ==========================
# 📂 Load URLs from file
# ==========================
def load_urls_from_file(filename):
    with open(filename, 'r') as file:
        return [url.strip() for url in file.readlines()]


# ==========================
# 🚀 Main Execution
# ==========================
if __name__ == "__main__":
    urls = load_urls_from_file('urls.txt')
    keyword = "free for"
    sent_links = load_sent_links()

    for url in urls:
        print(f"➡️ Checking {url}...")
        check_for_updates(url, keyword, sent_links)

    save_sent_links(sent_links)
    print("✅ Finished checking all URLs.")
