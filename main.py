import string
import time
import re
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from twocaptcha import TwoCaptcha  # For CAPTCHA solving
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

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
import time
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
import time
import random

def solve_captcha(browser, api_key):
    """Solve reCAPTCHA using 2Captcha with enhanced timing and debugging."""
    solver = TwoCaptcha(api_key)
    max_attempts = 5

    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt + 1}/{max_attempts}: Waiting for page to stabilize...")
            WebDriverWait(browser, 10).until(
                EC.invisibility_of_element_located((By.ID, "splash-screen"))
            )
            print("Splash screen gone, waiting for CAPTCHA to load...")
            time.sleep(30)  # Wait 30 seconds for page to settle

            # Log current HTML for debugging
            body_html = browser.find_element(By.TAG_NAME, "body").get_attribute('outerHTML')
            print(f"Attempt {attempt + 1} - Current body HTML before CAPTCHA check: {body_html[:15000]}")

            # Wait for CAPTCHA div
            print(f"Attempt {attempt + 1}: Checking for visible CAPTCHA div...")
            g_recaptcha = WebDriverWait(browser, 180).until(
                EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'g-recaptcha')]"))
            )
            site_key = g_recaptcha.get_attribute("data-sitekey")
            print(f"Found sitekey: {site_key}")

            # Switch to reCAPTCHA iframe
            iframe = WebDriverWait(browser, 180).until(
                EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'recaptcha')]"))
            )
            browser.switch_to.frame(iframe)
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'recaptcha-checkbox')]"))
            )
            browser.switch_to.default_content()

            # Solve CAPTCHA with 2Captcha
            captcha_result = solver.recaptcha(sitekey=site_key, url=browser.current_url)
            code = captcha_result['code']
            print(f"Received CAPTCHA response: {code[:20]}...")

            # Inject the response token
            browser.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{code}";')

            # Click "Next"
            next_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Next']"))
            )
            time.sleep(random.uniform(1, 3))
            next_button.click()

            print("CAPTCHA solved successfully!")
            return True

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            # Check for confirmation code field
            try:
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.NAME, "confirmation_code"))
                )
                print("Found confirmation code field instead of CAPTCHA, proceeding...")
                return True
            except:
                print("No confirmation code field found either.")
            if attempt + 1 < max_attempts:
                print("Retrying after delay...")
                time.sleep(30)
            else:
                print("All attempts failed.")
                return False

# Example usage
# browser = your_selenium_browser_instance
# api_key = "your_2captcha_api_key"
# solve_captcha(browser, api_key)

        except TimeoutException as e:
            print(f"Attempt {attempt + 1} failed with TimeoutException: {e}")
            # Check for alternative states
            try:
                code_field = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.NAME, "confirmation_code"))
                )
                print("Found confirmation code field instead of CAPTCHA, proceeding...")
                return True  # Skip CAPTCHA if code field is already present
            except (TimeoutException, NoSuchElementException):
                print("No confirmation code field found either.")
            attempt += 1
            if attempt < max_attempts:
                print("Retrying after delay...")
                time.sleep(20)  # Increase retry delay to 20 seconds
            else:
                print("All attempts failed. Final body HTML:", browser.find_element(By.TAG_NAME, "body").get_attribute('outerHTML')[:15000])
                return False
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            attempt += 1
            if attempt < max_attempts:
                print("Retrying after delay...")
                time.sleep(20)
            else:
                print("All attempts failed. Final body HTML:", browser.find_element(By.TAG_NAME, "body").get_attribute('outerHTML')[:15000])
                return False

def instagram_worker(browser, mail):
    """Automate Instagram signup with the temporary email and handle CAPTCHA after year selection."""
    try:
        browser.get('https://www.instagram.com/accounts/emailsignup/')
        time.sleep(random.uniform(2, 5))  # Random delay to mimic human loading

        # Handle cookies popup
        try:
            WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Allow all cookies']"))
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

        # Click Next button to trigger CAPTCHA
        next_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Next']"))
        )
        time.sleep(random.uniform(1, 3))
        next_button.click()
        print("Clicked the 'Next' button after year selection!")

        # Check for CAPTCHA after clicking Next
        api_key = "72fe002f79fbce126f36b6100dd6e847"  # Your 2Captcha API key
        try:
            if solve_captcha(browser, api_key):
                print("Proceeding after CAPTCHA resolution or code field detected...")
            else:
                print("Failed to solve CAPTCHA or detect code field, aborting...")
                return None
        except TimeoutException:
            print("No CAPTCHA or code field detected, proceeding...")
            return browser  # Proceed if no CAPTCHA or code field, might be an error state

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
    max_attempts = 10  # Retry up to 10 times
    attempt = 0
    while attempt < max_attempts:
        try:
            browser.get("https://tempmail.email/")
            print(f"Attempt {attempt + 1}: Checking for email...")
            WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Instagram')]"))
            )
            print("Found an email from Instagram!")
            codes = browser.find_elements(By.XPATH, "//div[contains(@class, 'message-body')]")
            if not codes:
                codes = browser.find_elements(By.XPATH, "//*[text()]")
                print("Falling back to broader text search...")
            for code in codes:
                text = code.text.strip()
                if text and re.search(r"\d{6}", text):
                    print(f"Raw email content: {text}")
                    return re.sub(r"\D", "", text)[:6]
            print("No code found in this attempt.")
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Waiting for confirmation code: {e}")
        attempt += 1
        time.sleep(random.uniform(5, 10))
    print("Failed to retrieve confirmation code after maximum attempts.")
    return None

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
            time.sleep(5)