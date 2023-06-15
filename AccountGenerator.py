from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium import webdriver
from random import randint
from environs import Env
from faker import Faker
import requests
import json
import time

Enviorment = Env(); Enviorment.read_env()

class CreateAccount():
    def __init__(self):
        self.driver = webdriver.Firefox(options=webdriver.FirefoxOptions().add_argument("--headless"))
    def load_webpage(self):
        self.driver.get("https://secure.byond.com/Join")
    def add_name(self, name):
        self.driver.find_element(by=By.NAME, value="account_name").send_keys(name)
    def add_password(self, password):
        self.driver.find_element(by=By.NAME, value="password").send_keys(password)
        self.driver.find_element(by=By.NAME, value="password_verify").send_keys(password)
    def add_email(self, email):
        self.driver.find_element(by=By.NAME, value="email").send_keys(email + "@1secmail.com")
    def agree_terms(self):
        self.driver.find_element(by=By.ID, value="joinage").click()
        self.driver.find_element(by=By.ID, value="joinagree").click()
        self.driver.find_element(by=By.LINK_TEXT, value="[Agree]").click()
    def finalize_join(self):
        self.driver.find_element(by=By.ID, value="joinbutton").click()
    def check_disabled(self):
        try:
            self.driver.find_element(by=By.CLASS_NAME, value="notice")
            self.driver.quit()
            return True
        except NoSuchElementException:
            self.driver.quit()
            return False
        
class VerifyAccount():
    def __init__(self, email):
        self.EmailAccount = json.loads(requests.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={email}&domain=1secmail.com").content.decode("utf-8"))
        self.Verified = False
        self.Email = email
    def wait_email(self):
        while self.Verified == False:
            self.EmailAccount = json.loads(requests.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={self.Email}&domain=1secmail.com").content.decode("utf-8"))
            time.sleep(1)
            if self.EmailAccount and self.EmailAccount[0] and self.EmailAccount[0]["subject"] == "BYOND Account Verification":
                self.Verified = True
                return self.__get_link(self.__get_content())
    def __get_content(self):
        return json.loads(requests.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={self.Email}&domain=1secmail.com&id=" + str(self.EmailAccount[0]["id"])).content.decode("utf-8"))["textBody"]
    def __get_link(self, content):
        return content[content.find("https://secure.byond.com/?command=email_verification"): content.find("\n\nIf you did not request this")]

class ControllerMain():
    def __init__(self):
        self.Username = Faker().first_name() + str(randint(30, 9999)) + Faker().last_name() + str(randint(1, 999))
        self.Password = Faker().first_name() + str(randint(9883033, 999090882))
        self.Email = Faker().first_name() + str(randint(9883033, 999090882)) + Faker().last_name()
        self.Driver = webdriver.Firefox()
        self.Disabled = False

        self.Account = CreateAccount()
        self.Verify = VerifyAccount(self.Email)
    def prompt_credientals(self, username="default"):
        if not username == "default":
            self.Username = username
    def create_account(self):
        self.Account.load_webpage()
        self.Account.add_name(self.Username)
        self.Account.add_password(self.Password)
        self.Account.add_email(self.Email)
        self.Account.agree_terms()
        self.Account.finalize_join()
    def check_disabled(self):
        if self.Account.check_disabled() == True:
            if Enviorment.bool("AUTOMATIC") == True:
                self.Disabled = True

                while self.Disabled == True:
                    print("Rate Limited: Waiting for " + Enviorment.str("FAILURE_TIMER") + " seconds")
                    time.sleep(Enviorment.int("FAILURE_TIMER"))

                    self.Account = CreateAccount()
                    self.create_account()

                    if self.Account.check_disabled() == False:
                        self.Disabled = False
            else:
                raise NoSuchElementException("You are currently rate limited by BYOND, please try again later")
    def verify_account(self):
        self.Driver.get(self.Verify.wait_email())
        self.Driver.quit()
    def post_webhook(self):
        json_dump = json.dumps({
        "embeds": [
        {
            "title": f"{self.Username}",
            "description": f"{self.Password}",
            "color": 155511,
        }
    ]
})
        requests.post(Enviorment.str("WEBHOOK"), headers={"Content-Type": "application/json"}, data=json_dump)

if Enviorment.bool("AUTOMATIC") == True:
    while True:
        control = ControllerMain()
        control.prompt_credientals()
        control.create_account()
        control.check_disabled()
        control.verify_account()
        control.post_webhook()
else:
    control = ControllerMain()
    user = input("Please provide a valid username\n")
    control.prompt_credientals(user)
    print("Creating User Account\n")
    control.create_account()
    print("Account Created\n")
    print("Checking Rate Limited Status\n")
    control.check_disabled()
    print("SUCCESS\n")
    print("Verifying User Account\n")
    control.verify_account()
    print("User Account Verified\n")
    control.post_webhook()
    print("Sent Status to Webhook\n")
    print("Account Created Successfully\n")

    input("\nPress and Key to Close...\n")
