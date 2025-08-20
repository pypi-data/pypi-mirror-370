import lugach.cvutils as cvu


def main():
    canvas = cvu.create_canvas_object()
    course = cvu.prompt_for_course(canvas)
    student = cvu.prompt_for_student(course)

    assignments = course.get_assignments(order_by="due_at")

    print()
    print(f"Grades for {student.name} in {course.name}:")
    print()

    total_score = 0
    total_points = 0
    for assignment in assignments:
        submission = assignment.get_submission(student.id)

        if submission and submission.workflow_state == "graded":
            print(
                f"{assignment.name:30.30} | {submission.score:4.0f} / {assignment.points_possible:<4.0f}"
            )
            total_score += submission.score
            total_points += assignment.points_possible
        else:
            print(
                f"{assignment.name:30.30} | ---- / {assignment.points_possible:<4.0f}"
            )

    print("----------------------------------------------")
    print(f"{'Total':<30} | {total_score:4.0f} / {total_points:<4.0f}")
    print()
    input("Press ENTER to continue.")

