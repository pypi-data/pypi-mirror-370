import lugach.thutils as thu


def _find_student_by_id(
    students: list[thu.Student], desired_student_id: int
) -> dict | None:
    for student in students:
        current_student_id = student["id"]
        if desired_student_id == current_student_id:
            return student


def get_tolerance_groups(
    auth_header: thu.AuthHeader, course: thu.Course, tolerance: int
) -> tuple[dict, dict]:
    students = thu.get_th_students(auth_header, course)
    attendance_proportions = thu.get_all_th_attendance_proportions_for_course(
        course, auth_header
    )

    students_under_tolerance = {}
    students_at_tolerance = {}
    for student_id, (attended, total) in attendance_proportions.items():
        classes_missed = total - attended
        if classes_missed < tolerance - 1:
            continue

        student = _find_student_by_id(students, student_id)
        if not student:
            print(f"Could not find student with id {student_id}")
            continue

        name = student["name"]
        if classes_missed == tolerance - 1:
            students_under_tolerance[name] = classes_missed
        else:
            students_at_tolerance[name] = classes_missed

    return (students_under_tolerance, students_at_tolerance)


def main():
    auth_header = thu.get_auth_header_for_session()
    course = thu.prompt_user_for_th_course(auth_header)
    tolerance = int(
        input("Enter the max number of absences for the course (generally 4): ")
    )

    students_under_tolerance, students_at_tolerance = get_tolerance_groups(
        auth_header, course, tolerance
    )

    s = "" if tolerance - 1 == 1 else "s"
    print()
    print(f"Here are all the students with {tolerance - 1} absence{s}: ")
    for student, absences in students_under_tolerance.items():
        print(f"    {student}: {absences}")

    s = "" if tolerance == 1 else "s"
    print()
    print(f"Here are all the students with {tolerance} or more absence{s}: ")
    for student, absences in students_at_tolerance.items():
        print(f"    {student}: {absences}")

    print()
    input("Press ENTER to quit.")

