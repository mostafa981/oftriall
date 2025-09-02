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
import datetime

SENT_FILE = "sent_links.txt"


# ==========================
# 📂 Sent Links Handling (per day)
# ==========================
def load_sent_links():
    if not os.path.exists(SENT_FILE):
        return {}
    sent = {}
    with open(SENT_FILE, "r") as f:
        for line in f:
            if "|" in line:
                url, date_str = line.strip().split("|", 1)
                sent[url] = date_str
    return sent


def save_sent_links(sent_links):
    with open(SENT_FILE, "w") as f:
        for url, date_str in sent_links.items():
            f.write(f"{url}|{date_str}\n")


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
# 🌐 Chrome Driver Setup
# ==========================
def make_driver():
    chrome_options = Options()
    chrome_bin = os.getenv("CHROME_PATH") or "/usr/bin/google-chrome"
    chrome_options.binary_location = chrome_bin

    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,1024")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver


# ==========================
# 🔍 Check Updates Function
# ==========================
def check_for_updates(url, keyword, sent_links):
    driver = make_driver()
    driver.get(url)

    today = datetime.date.today().isoformat()  # YYYY-MM-DD

    try:
        wait = WebDriverWait(driver, 20)
        subscribe_button = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".b-offer-join__btn, .m-rounded.m-flex.m-space-between.m-lg.g-btn")
            )
        )
        print(f"🔎 Found subscribe button on {url}")
        button_text = (subscribe_button.text or "").lower()

        last_sent = sent_links.get(url)

        if keyword.lower() in button_text:
            if last_sent == today:
                print(f"⏩ Already sent {url} today, skipping.")
            else:
                send_email(f"Update Found on {url}", f"There's a free offer available on {url}")
                sent_links[url] = today

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
