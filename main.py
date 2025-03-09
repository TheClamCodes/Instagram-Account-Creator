import string
import time
import re
import random
from playwright.sync_api import sync_playwright, Playwright
from twocaptcha import TwoCaptcha  # For CAPTCHA solving
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Simulate human-like mouse movements
def simulate_user_interaction(page):
    """Simulate human-like mouse movements and scrolling."""
    width, height = page.viewport_size["width"], page.viewport_size["height"]
    x, y = random.randint(10, width - 10), random.randint(10, height - 10)
    page.mouse.move(x, y, steps=random.randint(5, 15))
    scroll_amount = random.randint(100, 300)
    page.evaluate(f"window.scrollBy(0, {scroll_amount})")
    time.sleep(random.uniform(0.5, 1.5))

# Type text like a human
def human_like_type(page, selector, text):
    """Type text into an element character by character with small delays."""
    page.click(selector)
    for char in text:
        page.type(selector, char)
        time.sleep(random.uniform(0.05, 0.2))

# Retrieve temporary email
def get_mail(page):
    """Retrieve a temporary email address."""
    for _ in range(50):
        page.goto("https://tempmail.email/", wait_until="domcontentloaded")
        try:
            email = page.wait_for_selector(".email-block__genEmail", timeout=10000).inner_text()
            if email.strip():
                logger.info(f"Retrieved email: {email}")
                return email.strip()
        except Exception as e:
            logger.error(f"Error during mail retrieval: {e}")
        time.sleep(random.uniform(1, 3))
    logger.error("Failed to retrieve email.")
    return None

# Solve CAPTCHA with 2Captcha
def solve_captcha(page, api_key):
    """Solve reCAPTCHA with 2Captcha."""
    solver = TwoCaptcha(api_key)
    max_attempts = 5

    for attempt in range(max_attempts):
        try:
            logger.info(f"Attempt {attempt + 1}: Waiting for CAPTCHA...")
            time.sleep(random.uniform(2, 5))
            simulate_user_interaction(page)

            g_recaptcha = page.wait_for_selector("div.g-recaptcha", timeout=120000)
            site_key = g_recaptcha.get_attribute("data-sitekey")
            logger.info(f"Found sitekey: {site_key}")

            captcha_result = solver.recaptcha(sitekey=site_key, url=page.url)
            code = captcha_result["code"]
            logger.info(f"Received CAPTCHA response: {code[:20]}...")

            page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML = "{code}";')
            simulate_user_interaction(page)

            page.click("button:has-text('Next')", timeout=10000)
            logger.info("CAPTCHA solved successfully!")
            return True
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt + 1 < max_attempts:
                time.sleep(random.uniform(5, 10))
    logger.error("All CAPTCHA attempts failed.")
    return False

# Instagram signup process
def instagram_worker(page, mail):
    """Automate Instagram signup with anti-detection measures."""
    try:
        page.goto("https://www.instagram.com/accounts/emailsignup/", wait_until="domcontentloaded")
        time.sleep(random.uniform(2, 5))

        # Handle cookies popup
        try:
            page.click("button:has-text('Allow all cookies')", timeout=10000)
            logger.info("Allowed cookies.")
        except Exception:
            logger.info("Cookies popup not found, continuing...")

        simulate_user_interaction(page)

        # Fill form fields
        human_like_type(page, "[name='emailOrPhone']", mail)
        human_like_type(page, "[name='password']", "toffee")
        human_like_type(page, "[name='fullName']", generate_random_full_name())
        human_like_type(page, "[name='username']", generate_random_username())

        simulate_user_interaction(page)

        page.click("button[type='submit']", timeout=10000)
        logger.info("Clicked the 'Sign Up' button!")

        # Handle birthday dropdown
        page.select_option("select[title='Year:']", "1990")
        time.sleep(random.uniform(1, 3))
        logger.info("Selected year: 1990")

        page.click("button:has-text('Next')", timeout=10000)
        logger.info("Clicked 'Next' after year selection!")

        # Solve CAPTCHA
        api_key = "72fe002f79fbce126f36b6100dd6e847"  # Replace with your 2Captcha API key
        if solve_captcha(page, api_key):
            logger.info("Proceeding after CAPTCHA resolution...")
        else:
            logger.error("Failed to solve CAPTCHA.")
            return None

        return page
    except Exception as e:
        logger.error(f"Error during Instagram signup: {e}")
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
def confirm_code_mail(page):
    """Retrieve confirmation code from email."""
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            page.goto("https://tempmail.email/", wait_until="domcontentloaded")
            logger.info(f"Attempt {attempt + 1}: Checking for email...")
            page.wait_for_selector("//*[contains(text(), 'Instagram')]", timeout=20000)
            codes = page.query_selector_all(".message-body")
            for code in codes:
                text = code.inner_text().strip()
                match = re.search(r"\d{6}", text)
                if match:
                    return match.group(0)
        except Exception as e:
            logger.error(f"Waiting for confirmation code: {e}")
        time.sleep(random.uniform(5, 10))
    logger.error("Failed to retrieve confirmation code.")
    return None

# Complete signup with confirmation code
def signup(page, confirm_code):
    """Enter confirmation code and complete signup."""
    try:
        human_like_type(page, "[name='confirmation_code']", confirm_code)
        time.sleep(random.uniform(1, 3))
        page.click("button:has-text('Next')", timeout=10000)
        logger.info("Signup completed successfully.")
        return page
    except Exception as e:
        logger.error(f"Error during signup: {e}")
        return None

# Main execution with Playwright
def main():
    """Orchestrate the signup process with Playwright and anti-detection."""
    with sync_playwright() as p:
        # Launch browser with stealth configuration
        browser = p.chromium.launch(headless=False)  # Set to True for headless mode
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York",
            java_script_enabled=True,
            # Spoof WebGL and canvas fingerprint
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        # Apply additional stealth measures
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """)

        page1 = context.new_page()  # For email
        page2 = context.new_page()  # For Instagram signup

        try:
            mail = get_mail(page1)
            if mail:
                page2 = instagram_worker(page2, mail)
                if page2:
                    confirm_code = confirm_code_mail(page1)
                    if confirm_code:
                        signup(page2, confirm_code)
        finally:
            browser.close()

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(5)