import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Define mobile emulation settings
mobile_emulation = {
    "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
    "userAgent": "Mozilla/5.0 (Linux; Android 7.3.0; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
}

# Set Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)


def get_mail(browser):
    for _ in range(50):  # Retry logic for reliability
        browser.get("https://tempmail.email/")

        try:
            # Wait for email element to be present
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "email-block__genEmail"))
            )

            # Find the element containing the email address
            element = browser.find_element(By.CLASS_NAME, "email-block__genEmail")

            # Return the email if it's not empty
            if element and element.text.strip() != "":
                return element.text.strip()
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error during mail retrieval: {e}")

    return None  # Return None if email is not retrieved after retries


def main():
    browser_1 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    mail = get_mail(browser_1)
    if mail is None:
        print("Failed to get mail")
        browser_1.quit()
        return

    # Simulate further logic if mail is successfully retrieved
    print(f"Retrieved email: {mail}")
    browser_1.quit()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Error: {e}")
