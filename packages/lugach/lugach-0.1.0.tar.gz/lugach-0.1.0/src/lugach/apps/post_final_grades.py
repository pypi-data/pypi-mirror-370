import lugach.lhutils as lhu
import lugach.cvutils as cvu
import lugach.constants as cs

WARNING_MESSAGE = """\
    ▲ WARNING: THIS PROGRAM WILL POST FINAL GRADES FOR 
    THE CLASS THAT YOU SELECT! ▲

    Please make sure that you have permission to post
    final grades before continuing.

    Do you want to continue (y/n)? \
"""


def get_grade_from_points(points):
    for grade, _range in cs.GRADE_RANGES:
        if points in _range:
            return grade

    return "F"


def post_final_grades(course_sis_id, lh_auth_header, students):
    for i, student in enumerate(students):
        name = student["firstName"] + " " + student["lastName"]

        status = student["status"]
        if status == "REMOVED":
            print(f"Student {name} was removed from the course... ({i} so far)")
            continue

        activity = student["daysSinceLastActivity"]
        if activity >= 21:
            print(f"Student {name} had 21 days of inactivity... ({i} so far)")
            continue

        points = student["points"]
        if points == 0:
            print(f"Student {name} had 0 points... ({i} so far)")
            continue

        grade = student["finalGrade"]
        if grade:
            print(f"Student {name} already has grade {grade} assigned... ({i} so far)")
            continue
        else:
            grade = get_grade_from_points(points)

        final_grade_posted = lhu.post_final_grade(
            course_sis_id, lh_auth_header, student, grade
        )
        if not final_grade_posted:
            print(f"Final grade failed to post for {student}... ({i} so far)")
            continue

        print(
            f"Posted final grade {grade} for student {name} with {points} points... ({i} so far)"
        )


def main():
    start_application = input(WARNING_MESSAGE)
    if start_application != "y":
        return

    canvas = cvu.create_canvas_object()
    course = cvu.prompt_for_course(canvas)

    username, password = lhu.get_liberty_credentials()
    course_sis_id, lh_auth_header = lhu.get_lh_auth_credentials_for_session(
        course, username, password
    )

    students = lhu.get_lh_students(course_sis_id, lh_auth_header)

    continue_to_post_grades = input(f"Post grades for {course['course_name']} (y/n)? ")
    if continue_to_post_grades != "y":
        return

    post_final_grades(course_sis_id, lh_auth_header, students)

