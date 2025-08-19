import lugach.constants as cs
import lugach.cvutils as cvu
import lugach.lhutils as lhu
import requests
from canvasapi.user import User

def find_cv_student_from_lh_student(course, lh_student: dict) -> User | None:
    luid = lh_student["luId"]

    cv_students = list(course.get_users(search_term=luid))
    cv_students_len = len(cv_students)

    if cv_students_len == 0:
        return None
    elif cv_students_len > 1:
        print(f"The query for LU id {luid} returned {cv_students_len} results.")
        print("Here are their names:")
        for index, cv_student in enumerate(cv_students, start=1):
            print(f"{index}. {cv_student.name}")

        index = int(input(f"Enter the index of the student with LU id {luid}: "))
        return cv_students[index - 1]
    else:
        return cv_students[0]

def main():
    username, password = lhu.get_liberty_credentials()
    canvas = cvu.create_canvas_object()
    course = cvu.prompt_for_course(canvas)

    course_sis_id, lh_auth_header = lhu.get_lh_auth_credentials_for_session(course, username, password)
    all_students = lhu.get_lh_students(course_sis_id, lh_auth_header)

    continue_to_update_attendance_verification = input(f"Update attendance verification for {course["course_name"]} (y/n)? ")
    if continue_to_update_attendance_verification != "y":
        return

    for num_students, lh_student in enumerate(all_students, start=1):
        name = f"{lh_student["firstName"]} {lh_student["lastName"]}"

        if lh_student["status"] == "REMOVED" or lh_student["attendance"] == "ATTENDED":
            print(f"Skipped {name}... ({num_students} processed so far)")
            continue

        cv_student = find_cv_student_from_lh_student(course, lh_student)
        if not cv_student:
            print(f"No Canvas student found that matches {name}... ({num_students} processed so far)")
            continue

        submission = list(course.get_multiple_submissions(student_ids=[cv_student.id], workflow_state="graded"))
        if not submission:
            print(f"No submissions for {name}... ({num_students} processed so far)")
            continue

        attendance_url = f"https://lighthouse.okd.liberty.edu/rest/enrollments/{lh_student["id"]}/attendance?courseSisId={course_sis_id}&sis=banner&lms=canvas_lu"
        payload = {
            "attendance": "ATTENDED"
        }
        for i in range(1, cs.RELOAD_ATTEMPTS + 1):
            response = requests.post(url=attendance_url, json=payload, headers=lh_auth_header)
            if response.status_code != 200:
                print(f"{response.request.method} request returned with code {response.status_code}; retrying... ({i} of {cs.RELOAD_ATTEMPTS} attempts so far)")
                continue

            print(f"Attendance updated for {name}... ({num_students} processed so far)")
            break
        else:
            print(f"Failed to update attendance for {name}... ({num_students} processed so far)")