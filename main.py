import string
import time
import re
import random
from playwright.sync_api import sync_playwright
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Simulate human-like mouse movements
def simulate_user_interaction(page):
    width, height = page.viewport_size["width"], page.viewport_size["height"]
    x, y = random.randint(10, width - 10), random.randint(10, height - 10)
    page.mouse.move(x, y, steps=random.randint(5, 15))
    scroll_amount = random.randint(100, 300)
    page.evaluate(f"window.scrollBy(0, {scroll_amount})")
    time.sleep(random.uniform(0.5, 1.5))


# Type text like a human
def human_like_type(page, selector, text):
    page.click(selector)
    for char in text:
        page.type(selector, char)
        time.sleep(random.uniform(0.05, 0.2))


# Retrieve temporary email and return the page instance
def get_mail(page):
    page.goto("https://tempmail.email/", wait_until="domcontentloaded")
    for _ in range(50):
        try:
            email = page.wait_for_selector(".email-block__genEmail", timeout=10000).inner_text()
            if email.strip():
                logger.info(f"Retrieved email: {email}")
                return email.strip(), page  # Return email and page
        except Exception as e:
            logger.error(f"Error during mail retrieval: {e}")
        time.sleep(random.uniform(1, 3))
    logger.error("Failed to retrieve email.")
    return None, page


# Instagram signup process up to CAPTCHA
def instagram_worker(page, mail):
    try:
        page.goto("https://www.instagram.com/accounts/emailsignup/", wait_until="domcontentloaded")
        time.sleep(random.uniform(2, 5))
        try:
            page.click("button:has-text('Allow all cookies')", timeout=10000)
            logger.info("Allowed cookies.")
        except Exception:
            logger.info("Cookies popup not found, continuing...")

        simulate_user_interaction(page)
        human_like_type(page, "[name='emailOrPhone']", mail)
        human_like_type(page, "[name='password']", "toffee")
        human_like_type(page, "[name='fullName']", generate_random_full_name())
        human_like_type(page, "[name='username']", generate_random_username())
        simulate_user_interaction(page)

        page.click("button[type='submit']", timeout=10000)
        logger.info("Clicked the 'Sign Up' button!")

        page.select_option("select[title='Year:']", "1990")
        time.sleep(random.uniform(1, 3))
        logger.info("Selected year: 1990")

        page.click("button:has-text('Next')", timeout=10000)
        logger.info("Clicked 'Next' after year selection!")

        # Pause for manual CAPTCHA solving
        logger.info("Please solve the CAPTCHA manually in the browser. Waiting for you to complete it...")
        page.wait_for_selector("[name='email_confirmation_code']", timeout=300000)  # 5-minute timeout
        logger.info("CAPTCHA solved manually. Proceeding with automation...")

        return page
    except Exception as e:
        logger.error(f"Error during Instagram signup: {e}")
        return None


# Check for confirmation code using the existing page instance without refreshing
def confirm_code_mail(page):
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            logger.info(f"Attempt {attempt + 1}: Checking for email...")
            # Find all email entries
            emails = page.query_selector_all(".receivedMail-content-cover")
            for email in emails:
                sender = email.query_selector(".receivedMail-content__sender")
                if sender and "Instagram" in sender.inner_text():
                    subject = email.query_selector(".receivedMail-content__subject")
                    if subject:
                        text = subject.inner_text().strip()
                        match = re.search(r"\d{6}", text)
                        if match:
                            logger.info(f"Found confirmation code: {match.group(0)}")
                            return match.group(0)
            logger.warning("No Instagram email found in this attempt. Waiting before retry...")
        except Exception as e:
            logger.error(f"Waiting for confirmation code: {e}")
            page_content = page.content()
            with open("email_debug.html", "w", encoding="utf-8") as f:
                f.write(page_content)
            logger.info("Email page content saved to 'email_debug.html'.")
        time.sleep(random.uniform(5, 10))  # Wait between attempts without refreshing
    logger.error("Failed to retrieve confirmation code after all attempts.")
    return None


# Generate random full name
def generate_random_full_name():
    first_names = ['Aurelius', 'Zephyr', 'Odessa', 'Calliope', 'Evangeline']
    last_names = ['Moonstone', 'Foxworth', 'Wilde', 'Everest', 'Holloway']
    return f"{random.choice(first_names)} {random.choice(last_names)}"


# Generate random username
def generate_random_username():
    adjectives = ['witty', 'quirky', 'zesty', 'snarky', 'jumpy']
    nouns = ['platypus', 'marmot', 'gecko', 'narwhal', 'quokka']
    random_suffix = ''.join(random.choices(string.digits + string.ascii_lowercase, k=4))
    return f"{random.choice(adjectives)}_{random.choice(nouns)}_{random_suffix}"


# Complete signup with confirmation code
def signup(page, confirm_code):
    try:
        human_like_type(page, "[name='email_confirmation_code']", confirm_code)
        time.sleep(random.uniform(1, 3))
        page.click("button:has-text('Next')", timeout=10000)
        logger.info("Signup completed successfully.")
        return page
    except Exception as e:
        logger.error(f"Error during signup: {e}")
        return None


# Main execution
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Must be visible for manual CAPTCHA
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York",
            java_script_enabled=True,
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """)
        page1 = context.new_page()  # For email
        page2 = context.new_page()  # For Instagram signup

        try:
            mail, email_page = get_mail(page1)  # Get email and keep page instance
            if mail:
                page2 = instagram_worker(page2, mail)
                if page2:
                    confirm_code = confirm_code_mail(email_page)  # Use same page instance
                    if confirm_code:
                        signup(page2, confirm_code)
        finally:
            input("Press Enter to close the browser after signup is complete...")
            browser.close()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(5)