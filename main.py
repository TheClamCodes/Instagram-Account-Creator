import string
import time
import re
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import undetected_chromedriver as uc

# Define mobile emulation settings
mobile_emulation = {
    "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
    "userAgent": "Mozilla/5.0 (Linux; Android 7.3.0; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
}

# Set Chrome options
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)


def get_mail(browser):
    """ Retrieve temporary email using the browser instance. """
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


def instagram_worker(browser, mail):
    """ Automate Instagram signup with the temporary email. """
    try:
        browser.get('https://www.instagram.com/accounts/emailsignup/')

        # Wait for potential cookie acceptance button and click if present
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[text()='Allow essential cookies']"))
            ).click()
            print("Allowed cookies.")
        except TimeoutException:
            print("Cookies acceptance button not found, continuing...")

        # Enter the email address
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "emailOrPhone"))
        ).send_keys(mail)

        # Enter the email address
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        ).send_keys("toffee")

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "fullName"))
        ).send_keys(generate_random_full_name())

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(generate_random_username())

        # sign_up_button = WebDriverWait(browser, 10).until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, "button._acan._acap._acas"))
        # )

        print(f"HERE")

        # sign_up_button = WebDriverWait(browser, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign Up')]"))
        # )

        sign_up_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )

        print(f"Sign Up Button is displayed: {sign_up_button.is_displayed()}")
        print(f"Sign Up Button is enabled: {sign_up_button.is_enabled()}")
        print(f"Sign Up Button HTML: {sign_up_button.get_attribute('outerHTML')}")

        # Click the button
        sign_up_button.click()

        print("Clicked the 'Sign Up' button!")

        dropdown = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//select[@title='Year:']"))
        )

        # Create a Select object for the dropdown
        select = Select(dropdown)

        # Select the desired year, e.g., 1990
        select.select_by_value("1990")

        # Optionally, print the currently selected value for debugging
        selected_option = select.first_selected_option
        print(f"Selected year: {selected_option.text}")

        next_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Next']"))
        )

        # Wait for the button to become clickable
        WebDriverWait(browser, 10).until(
            lambda driver: not next_button.get_attribute("disabled")
        )

        # Click the button
        next_button.click()
        # Simulate filling other necessary fields (like fullname, username, password)
        # Example:
        # WebDriverWait(browser, 10).until(
        #     EC.presence_of_element_located((By.NAME, "fullname"))
        # ).send_keys("Full Name Placeholder")

        # print("Email entered successfully in Instagram signup.")
        return browser  # Return the browser if successful
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error during Instagram worker: {e}")
        return None  # Return None on failure


def generate_random_full_name():
    # Lists of random first names and last names
    first_names = [
        'Aurelius', 'Zephyr', 'Odessa', 'Calliope', 'Evangeline',
        'Lysander', 'Magnolia', 'Orion', 'Peregrine', 'Seraphina'
    ]
    last_names = [
        'Moonstone', 'Foxworth', 'Wilde', 'Everest', 'Holloway',
        'Darkmoor', 'Brightmore', 'Winterfell', 'Ravenwood', 'Stormchaser'
    ]

    # Pick a random first name and last name
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)

    # Combine them to form a full name
    return f"{first_name} {last_name}"

def generate_random_username():
    # Unusual adjectives and nouns for the username
    adjectives = ['witty', 'quirky', 'zesty', 'snarky', 'jumpy', 'gleeful', 'peculiar', 'loopy', 'spunky', 'breezy']
    nouns = ['platypus', 'marmot', 'gecko', 'narwhal', 'quokka', 'sloth', 'pangolin', 'axolotl', 'capybara', 'robin']

    # Pick a random adjective and noun
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)

    # Generate a random number or string suffix for uniqueness
    random_suffix = ''.join(random.choices(string.digits + string.ascii_lowercase, k=4))  # Mix of digits and letters

    # Concatenate to form the username
    return f"{adjective}_{noun}_{random_suffix}"

def confirm_code_mail(browser):
    """ Wait for the confirmation code to arrive in the inbox. """
    while True:
        try:
            # Locate the element containing the confirmation code
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

        time.sleep(2)  # Wait briefly before refreshing


def signup(browser, confirm_code):
    """ Complete the signup process with the confirmation code. """
    try:
        # Fill in the confirmation code during the signup process
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "confirmation_code"))
        ).send_keys(confirm_code)

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='Next']"))
        ).click()

        print("Signup completed successfully.")
        return browser
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error during signup process: {e}")
        return None


def main():
    browser_service = Service(ChromeDriverManager().install())

    # Create browser instances
    browser_1 = webdriver.Chrome(service=browser_service, options=chrome_options)
    browser_2 = webdriver.Chrome(service=browser_service, options=chrome_options)

    try:
        # Fetch temporary email
        mail = get_mail(browser_1)
        if mail is None:
            print("Failed to get mail.")
            return

        print(f"Retrieved email: {mail}")
        # Perform Instagram signup
        browser_2 = instagram_worker(browser_2, mail)
        if browser_2 is None:
            print("Failed to initiate Instagram signup.")
            return

        # Retrieve confirmation code from temporary email
        confirm_code = confirm_code_mail(browser_1)
        if not confirm_code:
            print("Failed to retrieve confirmation code.")
            return

        # Complete signup process
        browser_2 = signup(browser_2, confirm_code)

    finally:
        if browser_1:
            browser_1.delete_all_cookies()
            browser_1.quit()
        if browser_2:
            browser_2.delete_all_cookies()
            browser_2.quit()

    # finally:
    #     # Clean up resources
    #     browser_1.delete_all_cookies()
    #     browser_2.delete_all_cookies()
    #     browser_1.quit()
    #     browser_2.quit()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Error: {e}")
