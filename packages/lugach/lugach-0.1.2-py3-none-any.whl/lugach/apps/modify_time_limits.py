"""
A command line script that automatically applies quiz/test time limit accomodations
for a given student in a given Canvas course.
"""

import lugach.cvutils as cvu


def main():
    canvas = cvu.create_canvas_object()
    course = cvu.prompt_for_course(canvas)

    while True:
        print()
        student = cvu.prompt_for_student(course)

        print()
        while True:
            try:
                percentage = input(
                    "Enter the percentage of time to add (e.g. '50' for 50%): "
                )
                time_multiplier = int(percentage) / 100

                break
            except ValueError:
                print("Invalid input, try again.")

        cvu.set_time_limits_for_quizzes(course, student, time_multiplier)

        print()
        keep_looping = input(
            f"Would you like to modify accomodations for another student in {course.name}? (y/n): "
        )
        if keep_looping != "y":
            break

