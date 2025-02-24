import string
import time
import re
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains  # For mouse movements
from twocaptcha import TwoCaptcha  # For CAPTCHA solving
import undetected_chromedriver as uc  # Used to avoid bot detection

# Define Chrome options with anti-detection measures
def get_chrome_options():
    """Generate ChromeOptions with anti-detection settings."""
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Hides automation flags
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Set a custom user agent to mimic a real browser
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return options

# Simulate human-like interactions
def simulate_user_interaction(browser):
    """Simulate mouse movements and scrolling to mimic human behavior."""
    actions = ActionChains(browser)
    # Move mouse to a random position
    actions.move_by_offset(random.randint(10, 100), random.randint(10, 100)).perform()
    # Generate random scroll amount in Python
    scroll_amount = random.randint(100, 200)
    # Execute the JavaScript with the Python-generated value
    browser.execute_script(f"window.scrollBy(0, {scroll_amount});")
    # Add a random pause
    time.sleep(random.uniform(0.5, 1.5))

# Type text like a human
def human_like_send_keys(element, text):
    """Type text into an element character by character with small delays."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

# Retrieve temporary email
def get_mail(browser):
    """Retrieve a temporary email address."""
    for _ in range(50):
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

# Solve CAPTCHA with anti-detection
def solve_captcha(browser, api_key):
    """Solve reCAPTCHA with 2Captcha, incorporating human-like behavior."""
    solver = TwoCaptcha(api_key)
    max_attempts = 5
    wait_time = 120  # Increased from 60 to 120 seconds

    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt + 1}: Waiting for CAPTCHA to load...")
            time.sleep(random.uniform(2, 5))  # Random delay for page stabilization

            # Simulate user interaction before locating CAPTCHA
            simulate_user_interaction(browser)

            # Wait for CAPTCHA div with increased timeout
            g_recaptcha = WebDriverWait(browser, wait_time).until(
                EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'g-recaptcha')]"))
            )
            site_key = g_recaptcha.get_attribute("data-sitekey")
            print(f"Found sitekey: {site_key}")

            # Solve CAPTCHA using 2Captcha
            captcha_result = solver.recaptcha(sitekey=site_key, url=browser.current_url)
            code = captcha_result['code']
            print(f"Received CAPTCHA response: {code[:20]}...")

            # Inject CAPTCHA response into the page
            browser.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{code}";')

            # Simulate interaction after solving CAPTCHA
            simulate_user_interaction(browser)

            # Click "Next" button
            next_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Next']"))
            )
            time.sleep(random.uniform(1, 3))
            next_button.click()
            print("CAPTCHA solved successfully!")
            return True

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt + 1 < max_attempts:
                print("Retrying after delay...")
                time.sleep(random.uniform(5, 10))
            else:
                print("All CAPTCHA attempts failed.")
                return False

# Instagram signup process
def instagram_worker(browser, mail):
    """Automate Instagram signup with anti-detection measures."""
    try:
        browser.get('https://www.instagram.com/accounts/emailsignup/')
        time.sleep(random.uniform(2, 5))  # Random delay for page load

        # Handle cookies popup
        try:
            cookie_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Allow all cookies']"))
            )
            time.sleep(random.uniform(1, 3))
            cookie_button.click()
            print("Allowed cookies.")
        except TimeoutException:
            print("Cookies popup not found, continuing...")

        # Simulate interaction before form filling
        simulate_user_interaction(browser)

        # Fill form fields with human-like typing
        email_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "emailOrPhone"))
        )
        human_like_send_keys(email_field, mail)
        time.sleep(random.uniform(1, 2))

        password_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        human_like_send_keys(password_field, "toffee")
        time.sleep(random.uniform(1, 2))

        full_name_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "fullName"))
        )
        human_like_send_keys(full_name_field, generate_random_full_name())
        time.sleep(random.uniform(1, 2))

        username_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        human_like_send_keys(username_field, generate_random_username())
        time.sleep(random.uniform(1, 2))

        # Simulate interaction before clicking sign-up
        simulate_user_interaction(browser)

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
        time.sleep(random.uniform(1, 3))
        print(f"Selected year: {select.first_selected_option.text}")

        # Simulate interaction before clicking Next
        # simulate_user_interaction(browser)

        # Click Next to trigger CAPTCHA
        next_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Next']"))
        )
        time.sleep(random.uniform(1, 3))
        next_button.click()
        print("Clicked 'Next' after year selection!")

        # Solve CAPTCHA
        api_key = "72fe002f79fbce126f36b6100dd6e847"  # Replace with your 2Captcha API key
        if solve_captcha(browser, api_key):
            print("Proceeding after CAPTCHA resolution...")
        else:
            print("Failed to solve CAPTCHA.")
            return None

        return browser
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error during Instagram signup: {e}")
        return None

# Generate random full name
def generate_random_full_name():
    """Generate a random full name."""
    first_names = ['Aurelius', 'Zephyr', 'Odessa', 'Calliope', 'Evangeline']
    last_names = ['Moonstone', 'Foxworth', 'Wilde', 'Everest', 'Holloway']
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# Generate random username
def generate_random_username():
    """Generate a random username."""
    adjectives = ['witty', 'quirky', 'zesty', 'snarky', 'jumpy']
    nouns = ['platypus', 'marmot', 'gecko', 'narwhal', 'quokka']
    random_suffix = ''.join(random.choices(string.digits + string.ascii_lowercase, k=4))
    return f"{random.choice(adjectives)}_{random.choice(nouns)}_{random_suffix}"

# Check for confirmation code
def confirm_code_mail(browser):
    """Retrieve confirmation code from email."""
    max_attempts = 10
    attempt = 0
    while attempt < max_attempts:
        try:
            browser.get("https://tempmail.email/")
            print(f"Attempt {attempt + 1}: Checking for email...")
            WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Instagram')]"))
            )
            codes = browser.find_elements(By.XPATH, "//div[contains(@class, 'message-body')]")
            for code in codes:
                text = code.text.strip()
                if text and re.search(r"\d{6}", text):
                    return re.sub(r"\D", "", text)[:6]
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Waiting for confirmation code: {e}")
        attempt += 1
        time.sleep(random.uniform(5, 10))
    print("Failed to retrieve confirmation code.")
    return None

# Complete signup with confirmation code
def signup(browser, confirm_code):
    """Enter confirmation code and complete signup."""
    try:
        code_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "confirmation_code"))
        )
        human_like_send_keys(code_field, confirm_code)
        time.sleep(random.uniform(1, 3))
        next_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']"))
        )
        time.sleep(random.uniform(1, 3))
        next_button.click()
        print("Signup completed successfully.")
        return browser
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error during signup: {e}")
        return None

# Main execution
def main():
    """Orchestrate the signup process with anti-detection."""
    browser_1 = uc.Chrome(options=get_chrome_options())
    browser_2 = uc.Chrome(options=get_chrome_options())
    try:
        mail = get_mail(browser_1)
        if mail:
            print(f"Retrieved email: {mail}")
            # Hide webdriver property
            browser_2.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            browser_2 = instagram_worker(browser_2, mail)
            if browser_2:
                confirm_code = confirm_code_mail(browser_1)
                if confirm_code:
                    browser_2 = signup(browser_2, confirm_code)
    finally:
        if browser_1:
            browser_1.quit()
        if browser_2:
            browser_2.quit()

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)