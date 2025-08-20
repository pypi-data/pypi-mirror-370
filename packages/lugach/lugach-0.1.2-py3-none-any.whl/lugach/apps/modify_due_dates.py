import lugach.cvutils as cvu

from dateutil.parser import parse
from datetime import datetime
from dateutil.parser import ParserError


def get_new_due_date() -> datetime:
    while True:
        try:
            date_query = input("Type a value for the new due date (mm-dd-YYYY): ")
            new_due_date = parse(date_query)
            confirm_date = input(f"Confirm new date as {new_due_date} (y/n)? ")
            if confirm_date == "y":
                return new_due_date
        except ParserError:
            print("Please enter a date in the proper format.")


def main():
    canvas = cvu.create_canvas_object()
    course = cvu.prompt_for_course(canvas)

    while True:
        print()
        student = cvu.prompt_for_student(course)
        print()
        assignment = cvu.prompt_for_assignment(course)
        print()

        old_due_date = cvu.get_assignment_or_quiz_due_date(course, assignment)
        print(f"The current due date is {old_due_date}.")

        new_due_date = get_new_due_date()
        assignment.create_override(
            assignment_override={
                "student_ids": [student.id],
                "title": student.name,
                "due_at": new_due_date,
                "lock_at": new_due_date,
            }
        )

        print(f"Due date updated! The new due date is {new_due_date}.")
        print()

        keep_looping = input(
            f"Would you like to modify due dates for another student in {course.name}? (y/n): "
        )
        if keep_looping != "y":
            break

