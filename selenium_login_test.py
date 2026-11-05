from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


URL = "http://localhost:3000/"
USERNAME = "raj23"
PASSWORD = "12345678"
WRONG_PASSWORD = "123456"

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)


def login(password):
    driver.get(URL)
    wait.until(EC.visibility_of_element_located((By.NAME, "username"))).send_keys(USERNAME)
    wait.until(EC.visibility_of_element_located((By.NAME, "password"))).send_keys(password)
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
    ).click()


try:
    login(WRONG_PASSWORD)
    error = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "login-error")))
    assert error.is_displayed(), "Unsuccessful login should show an error."
    print("Unsuccessful login passed.")

    login(PASSWORD)
    dashboard = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//*[@data-testid='dashboard']"))
    )
    assert dashboard.is_displayed(), "Successful login should show the dashboard."
    print("Successful login passed.")
finally:
    driver.quit()
