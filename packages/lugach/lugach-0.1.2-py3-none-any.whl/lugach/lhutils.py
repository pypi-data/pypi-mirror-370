import requests
import lugach.constants as cs

from canvasapi.course import Course

from getpass import getpass

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from lugach.secrets import get_credentials, set_credentials

CREDENTIALS_ID = "LU_LIGHTHOUSE"


def get_liberty_credentials() -> tuple[str, str]:
    LIBERTY_CREDENTIALS = get_credentials(CREDENTIALS_ID)
    return LIBERTY_CREDENTIALS


def prompt_user_for_liberty_credentials():
    while True:
        try:
            get_credentials(CREDENTIALS_ID)
            print("Liberty credentials provided!")

            should_update_liberty_credentials = input(
                "Would you like to update them (y/n)? "
            )
            if should_update_liberty_credentials == "y":
                raise PermissionError("User asked to update their credentials.")

            return
        except (NameError, PermissionError) as e:
            print(e)
            username = input("Enter your Liberty username: ")
            password = getpass("Enter your Liberty password: ")
            set_credentials(id=CREDENTIALS_ID, username=username, password=password)


def get_lh_auth_credentials_for_session(
    course: Course, liberty_username: str, liberty_password: str
) -> tuple[str, dict[str, str]]:
    course_id = course.id

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(cs.GLOBAL_TIMEOUT_SECS)
    wait = WebDriverWait(driver, timeout=cs.GLOBAL_TIMEOUT_SECS)

    driver.get(f"https://canvas.liberty.edu/courses/{course_id}/external_tools/183/")

    username_input = driver.find_element(by=By.ID, value="i0116")
    username_input.send_keys(liberty_username)
    password_input = driver.find_element(by=By.ID, value="i0118")
    password_input.send_keys(liberty_password)

    submit = driver.find_element(by=By.ID, value="idSIButton9")
    wait.until(lambda d: submit.get_attribute("value") == "Next")
    submit.click()

    for i in range(1, cs.RELOAD_ATTEMPTS + 1):
        try:
            submit = driver.find_element(by=By.ID, value="idSIButton9")
            wait.until(lambda d: submit.get_attribute("value") == "Sign in")
            submit.click()
            break
        except (StaleElementReferenceException, TimeoutException):
            print(
                f"Failed to submit form, retrying... ({i} of {cs.RELOAD_ATTEMPTS} attempts so far)"
            )
    else:
        driver.quit()
        raise PermissionError("Failed to load authentication header.")

    wait.until(lambda d: "canvas" in d.current_url)
    course_sis_id_element = driver.find_element(by=By.ID, value="custom_course_sis_id")

    course_sis_id = course_sis_id_element.get_attribute("value")
    if course_sis_id is None:
        raise ValueError("Could not determine course_sis_id.")

    driver.get("https://lighthouse.okd.liberty.edu/")
    wait.until(lambda d: d.get_cookie("access_token"))

    access_token_cookie = driver.get_cookie("access_token")
    if access_token_cookie is None:
        raise PermissionError("Could not retrieve access token cookie.")

    access_token = access_token_cookie["value"]

    driver.quit()

    lh_auth_header = {"Authorization": f"Bearer {access_token}"}
    return course_sis_id, lh_auth_header


def get_lh_students(course_sis_id: str, lh_auth_header: dict[str, str]) -> list[dict]:
    students_url = f"https://lighthouse.okd.liberty.edu/rest/courses/{course_sis_id}/enrollments?courseSisId={course_sis_id}&sis=banner&lms=canvas_lu"

    for i in range(1, cs.RELOAD_ATTEMPTS + 1):
        response = requests.get(url=students_url, headers=lh_auth_header)
        if response.status_code != 200:
            print(
                f"{response.request.method} request returned with code {response.status_code}; retrying... ({i} of {cs.RELOAD_ATTEMPTS} attempts so far)"
            )
            continue

        break
    else:
        raise PermissionError("Failed to log into Lighthouse.")

    students = response.json()
    return students


def post_final_grade(course_sis_id, lh_auth_header, student, grade):
    if grade not in ["A", "B", "C", "D", "F"]:
        raise TypeError(
            "Expected a letter grade (A, B, C, D, or F) for the grade parameter."
        )

    id = student["id"]
    grades_url = f"https://lighthouse.okd.liberty.edu/rest/enrollments/{id}/grade?courseSisId={course_sis_id}&sis=banner&lms=canvas_lu"
    payload = {"grade": grade}

    for i in range(1, cs.RELOAD_ATTEMPTS + 1):
        response = requests.post(url=grades_url, json=payload, headers=lh_auth_header)
        if response.status_code != 200:
            print(
                f"{response.request.method} request returned with code {response.status_code}; retrying... ({i} of {cs.RELOAD_ATTEMPTS} attempts so far)"
            )
            continue

        break
    else:
        raise PermissionError("Failed to log into Lighthouse.")

    return True
