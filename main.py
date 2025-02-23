import string
import time
import re
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc  # Used to avoid bot detection

# Define mobile emulation settings (optional, uncomment if needed)
mobile_emulation = {
    "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
    "userAgent": "Mozilla/5.0 (Linux; Android 7.3.0; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
}

def get_chrome_options():
    """Generate a fresh ChromeOptions object."""
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Hides automation flag
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_experimental_option("mobileEmulation", mobile_emulation)  # Uncomment for mobile emulation
    return options

def get_mail(browser):
    """Retrieve temporary email using the browser instance."""
    for _ in range(50):  # Retry logic for reliability
        browser.get("https://tempmail.email/")
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "email-block__genEmail"))
            )
            element = browser.find_element(By.CLASS_NAME, "email-block__genEmail")
            if element and element.text.strip() != "":
                return element.text.strip()
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error during mail retrieval: {e}")
        time.sleep(random.uniform(1, 3))  # Random delay before retry
    return None

def instagram_worker(browser, mail):
    """Automate Instagram signup with the temporary email."""
    try:
        browser.get('https://www.instagram.com/accounts/emailsignup/')
        time.sleep(random.uniform(2, 5))  # Random delay to mimic human loading

        # Handle cookies popup
        try:
            WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Allow essential cookies']"))
            ).click()
            time.sleep(random.uniform(1, 3))
            print("Allowed cookies.")
        except TimeoutException:
            print("Cookies acceptance button not found, continuing...")

        # Fill form with random delays
        email_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "emailOrPhone"))
        )
        time.sleep(random.uniform(0.5, 1.5))
        email_field.send_keys(mail)

        password_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        time.sleep(random.uniform(0.5, 1.5))
        password_field.send_keys("toffee")

        full_name_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "fullName"))
        )
        time.sleep(random.uniform(0.5, 1.5))
        full_name_field.send_keys(generate_random_full_name())

        username_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        time.sleep(random.uniform(0.5, 1.5))
        username_field.send_keys(generate_random_username())

        # Click sign-up button
        sign_up_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        time.sleep(random.uniform(1, 3))
        sign_up_button.click()
        print("Clicked the 'Sign Up' button!")

        # Handle birthday dropdown
        dropdown = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//select[@title='Year:']"))
        )
        select = Select(dropdown)
        select.select_by_value("1990")
        time.sleep(random.uniform(1, 2))
        print(f"Selected year: {select.first_selected_option.text}")

        next_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Next']"))
        )
        time.sleep(random.uniform(1, 3))
        next_button.click()

        # Optional CAPTCHA handling (uncomment and configure if needed)
        # api_key = "YOUR_2CAPTCHA_API_KEY"  # Replace with your 2Captcha API key
        # if solve_captcha(browser, api_key):
        #     print("CAPTCHA solved, proceeding...")
        #     time.sleep(random.uniform(2, 5))

        return browser
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error during Instagram worker: {e}")
        return None

def generate_random_full_name():
    """Generate a random full name."""
    first_names = ['Aurelius', 'Zephyr', 'Odessa', 'Calliope', 'Evangeline', 'Lysander', 'Magnolia', 'Orion', 'Peregrine', 'Seraphina']
    last_names = ['Moonstone', 'Foxworth', 'Wilde', 'Everest', 'Holloway', 'Darkmoor', 'Brightmore', 'Winterfell', 'Ravenwood', 'Stormchaser']
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_random_username():
    """Generate a random username."""
    adjectives = ['witty', 'quirky', 'zesty', 'snarky', 'jumpy', 'gleeful', 'peculiar', 'loopy', 'spunky', 'breezy']
    nouns = ['platypus', 'marmot', 'gecko', 'narwhal', 'quokka', 'sloth', 'pangolin', 'axolotl', 'capybara', 'robin']
    random_suffix = ''.join(random.choices(string.digits + string.ascii_lowercase, k=4))
    return f"{random.choice(adjectives)}_{random.choice(nouns)}_{random_suffix}"

def confirm_code_mail(browser):
    """Wait for the confirmation code to arrive in the inbox."""
    while True:
        try:
            browser.get("https://tempmail.email/")
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'message-body')]"))
            )
            codes = browser.find_elements(By.XPATH, "//div[contains(@class, 'message-body')]")
            if codes:
                for code in codes:
                    if code.text.strip():
                        return re.sub(r"\D", "", code.text.strip())
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Waiting for confirmation code: {e}")
        time.sleep(random.uniform(2, 5))  # Random delay before refreshing

def signup(browser, confirm_code):
    """Complete the signup process with the confirmation code."""
    try:
        code_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "confirmation_code"))
        )
        time.sleep(random.uniform(0.5, 1.5))
        code_field.send_keys(confirm_code)

        next_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']"))
        )
        time.sleep(random.uniform(1, 3))
        next_button.click()

        print("Signup completed successfully.")
        return browser
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error during signup process: {e}")
        return None

# Optional CAPTCHA solver (requires 2captcha-python package and API key)
# from twocaptcha import TwoCaptcha
# def solve_captcha(browser, api_key):
#     solver = TwoCaptcha(api_key)
#     try:
#         WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//div[@class='g-recaptcha']"))
#         )
#         site_key = browser.find_element(By.XPATH, "//div[@class='g-recaptcha']").get_attribute("data-sitekey")
#         captcha_result = solver.recaptcha(sitekey=site_key, url=browser.current_url)
#         code = captcha_result['code']
#         browser.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{code}";')
#         print("CAPTCHA solved successfully!")
#         return True
#     except Exception as e:
#         print(f"CAPTCHA solving failed: {e}")
#         return False

def main():
    """Main function to orchestrate the signup process."""
    browser_1 = uc.Chrome(options=get_chrome_options())
    browser_2 = uc.Chrome(options=get_chrome_options())

    try:
        mail = get_mail(browser_1)
        if mail:
            print(f"Retrieved email: {mail}")
            browser_2 = instagram_worker(browser_2, mail)
            if browser_2:
                confirm_code = confirm_code_mail(browser_1)
                if confirm_code:
                    browser_2 = signup(browser_2, confirm_code)
    finally:
        if browser_1:
            browser_1.delete_all_cookies()
            browser_1.quit()
        if browser_2:
            browser_2.delete_all_cookies()
            browser_2.quit()

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)  # Delay before retrying