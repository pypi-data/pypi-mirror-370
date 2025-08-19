import os
from datetime import datetime

from canvasapi.page import PaginatedList
import dotenv as dv
from canvasapi import Canvas
from canvasapi.assignment import Assignment
from canvasapi.course import Course
from canvasapi.exceptions import BadRequest, InvalidAccessToken
from canvasapi.quiz import Quiz
from canvasapi.user import User
from dateutil.parser import parse


def sanitize_string(string: str) -> str:
    """
    Returns a lowercase, whitespace-trimmed version of a given string.

    Parameters
    ----------
    `str`: string
        The string to sanitize.

    Returns
    -------
    string
        The result after sanitizing.
    """
    return string.strip().lower()


def course_name_with_date(course: Course) -> str:
    """
    Prepares courses to be queried by creating a string
    containing the course name and the start date.

    Parameters
    ----------
    `course`: [Course](https://canvasapi.readthedocs.io/en/stable/course-ref.html)
        The course to be converted to a name/date string representation.

    Returns
    -------
    string
        The string containing the course name and start date in the format "NNNNNNNNN (mm-yyyy)."
    """

    start_date = parse(course.start_at)
    return f"{course.name} ({start_date.month}-{start_date.year})"


def match_course(query: str, course: Course) -> bool:
    sanitized_query = sanitize_string(query)
    sanitized_course_name_with_date = sanitize_string(course_name_with_date(course))

    return sanitized_query in sanitized_course_name_with_date


def _create_env_file() -> bool:
    try:
        with open(".env", "w"):
            return True
    except OSError as e:
        raise OSError("Fatal error: failed to create new .env file.") from e


def _update_env_file(**kwargs: str) -> bool:
    try:
        path = dv.find_dotenv(raise_error_if_not_found=True)
        for key, value in kwargs.items():
            dv.set_key(dotenv_path=path, key_to_set=key, value_to_set=value)
        return True
    except IOError as e:
        raise IOError("Fatal error: did not find .env file.") from e


def _get_canvas_object_from_env_file() -> Canvas:
    try:
        path = dv.find_dotenv(raise_error_if_not_found=True)
    except IOError as e:
        raise FileNotFoundError("No .env file was found.") from e

    dv.load_dotenv(dotenv_path=path, override=True)
    API_URL = os.getenv("CANVAS_API_URL")
    API_KEY = os.getenv("CANVAS_API_KEY")
    if not API_URL or not API_KEY:
        raise NameError("Failed to load URL and key from .env file.")

    try:
        canvas = Canvas(API_URL, API_KEY)
        canvas.get_courses()[0]
    except InvalidAccessToken as e:
        raise InvalidAccessToken(
            "You entered an invalid API key in the .env file."
        ) from e

    return canvas


def create_canvas_object() -> Canvas:
    while True:
        try:
            canvas = _get_canvas_object_from_env_file()
            print("Canvas API key found!")
            return canvas
        except FileNotFoundError as e:
            print(e)
            _create_env_file()
        except (NameError, InvalidAccessToken) as e:
            print(e)
            api_key = input("Enter your API key from Canvas: ")
            _update_env_file(
                CANVAS_API_URL="https://canvas.liberty.edu", CANVAS_API_KEY=api_key
            )


def get_courses_from_canvas_object(
    canvas: Canvas, enrolled_as="designer", **kwargs
) -> PaginatedList:
    print("Loading courses from Canvas...")
    courses = canvas.get_courses(enrollment_type=enrolled_as, **kwargs)

    return courses


def filter_courses_by_query(courses: list[Course], query: str) -> list[Course]:
    init_courses = [course for course in courses if course.start_at]
    course_results = [course for course in init_courses if match_course(query, course)]

    return course_results


def prompt_for_course(canvas: Canvas) -> Course:
    """
    Uses a simple command line interface to prompt the user to choose a modifiable course.
    In order for a user to select a course, they must be added as a Designer to the course in Canvas.
    Additionally, the course must have a start date.

    Parameters
    ----------
    `canvas`: [Canvas](https://canvasapi.readthedocs.io/en/stable/canvas-ref.html).
        Provides access to the Canvas API, from which the function collects course data.

    Returns
    -------
    [Course](https://canvasapi.readthedocs.io/en/stable/course-ref.html)
        Points to the course the user chose.
    """

    all_course_results = [
        course for course in get_courses_from_canvas_object(canvas) if course.start_at
    ]
    course_results = all_course_results

    while True:
        print("Which course would you like to access?")
        print("The options are: \n")
        for course in course_results:
            print(f"    {course_name_with_date(course)}")

        query = input("\nChoose one of the above options: ")
        course_results = filter_courses_by_query(course_results, query)

        if len(course_results) == 0:
            print("No such course was found.")
            course_results = all_course_results
        elif len(course_results) == 1:
            course = course_results[0]
            print(f"You chose {course.name}.")
            return course


def filter_users_by_query(
    source: Course | list[User], query: str, enrolled_as="student"
) -> list[User]:
    if type(source) is Course:
        return list(source.get_users(search_term=query, enrollment_type=enrolled_as))
    elif type(source) is list:
        sanitized_query = sanitize_string(query)
        return [
            user for user in source if sanitized_query in sanitize_string(user.name)
        ]
    else:
        raise TypeError("Expected Course object or list")


def process_bad_request(e: BadRequest) -> bool:
    args_string = e.args[0]
    if type(args_string) is not str:
        raise e

    if "2 or more characters is required" not in args_string:
        raise e

    print("Too few characters, try again")
    return True


def prompt_for_student(course: Course) -> User:
    """
    Uses a simple command line interface to prompt the user to choose a student from a given course.

    Parameters
    ----------
    `course`: [Course](https://canvasapi.readthedocs.io/en/stable/course-ref.html)
        The course to pull student information from.

    Returns
    -------
    [User](https://canvasapi.readthedocs.io/en/stable/user-ref.html)
        Points to the student the user chose.
    """

    source = course
    while True:
        while True:
            try:
                query = input("Search for the student by name: ")
                source = filter_users_by_query(source, query)
                break
            except BadRequest as e:
                process_bad_request(e)

        source_len = len(source)
        if source_len == 0:
            print("\nNo such student was found.")
            source = course
            continue
        elif source_len == 1:
            selected_student = source[0]
            print(f"\nYou chose {selected_student.name}.")
            return selected_student

        print(f"\nYour query returned {source_len} students.")
        print("Here are their names:\n")
        for student in source:
            print(f"    {student.name}")
        print()


def filter_assignments_by_query(
    source: list[Assignment], query: str, has_due_date=True
) -> list[Assignment]:
    sanitized_query = sanitize_string(query)
    return [
        assignment
        for assignment in source
        if sanitized_query in sanitize_string(assignment.name)
    ]


def prompt_for_assignment(course: Course, has_due_date=True) -> Assignment:
    all_assignments = [
        assignment
        for assignment in course.get_assignments()
        if not has_due_date or assignment.due_at
    ]
    source = all_assignments

    while True:
        print("Which assignment would you like to access?")
        print("The options are:")
        print()
        for assignment in source:
            print(f"    {assignment.name}")
        print()

        query = input("Choose one of the above options: ")
        source = filter_assignments_by_query(source, query)

        if len(source) == 0:
            print("No such course was found.")
            source = all_assignments
        elif len(source) == 1:
            assignment = source[0]
            print(f"You chose {assignment.name}.")
            return assignment


def set_time_limit_for_quiz(student: User, quiz: Quiz, time_multiplier: float) -> None:
    if not quiz.time_limit:
        print(f"{quiz.title} has no time limit.")
        return

    extra_time = quiz.time_limit * time_multiplier

    print(f"Updating {quiz.title} (default time limit is {quiz.time_limit} minutes)...")

    quiz.set_extensions([{"user_id": student.id, "extra_time": extra_time}])

    print(
        f"{quiz.title} updated! {student.name} now has {extra_time} minutes extra on this quiz."
    )


def set_time_limits_for_quizzes(
    course: Course, student: User, time_multiplier: float
) -> None:
    """
    Updates the time limit extensions for all timed quizzes in the given course
    for the given student. They are set to `time_multiplier` times the default
    time limit for the quiz.

    Parameters
    ----------
    `course`: [Course](https://canvasapi.readthedocs.io/en/stable/course-ref.html)
        The course to pull quiz information from.

    `student`: [User](https://canvasapi.readthedocs.io/en/stable/user-ref.html)
        The student to modify time limit extensions for.

    `time_multiplier`: float
        The proportion of the time limit that should be added as a time limit
        extension for each quiz.
    """

    quizzes = [quiz for quiz in course.get_quizzes() if quiz.time_limit]

    for quiz in quizzes:
        set_time_limit_for_quiz(student, quiz, time_multiplier)


def get_assignment_or_quiz_due_date(course: Course, assignment: Assignment) -> datetime:
    if assignment.is_quiz_assignment:
        quiz_id = assignment.quiz_id
        quiz = course.get_quiz(quiz_id)
        due_date = parse(quiz.due_at)
    else:
        due_date = parse(assignment.due_at)

    return due_date
