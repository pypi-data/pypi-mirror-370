import lugach.thutils as thu


def convert_attendance_record_to_str(attendance_record: dict):
    attendance_indicator = (
        "✅"
        if attendance_record["attended"]
        else "🆗"
        if attendance_record["excused"]
        else "❌"
    )
    return f"( {attendance_indicator} ) {attendance_record['date_taken']}"


def list_attendance_records(attendance_records: list[dict]):
    for i, record in enumerate(attendance_records, start=1):
        print(f"{i:4}. {convert_attendance_record_to_str(record)}")


def prompt_user_for_attendance_record_to_edit(attendance_records: list[dict]) -> dict:
    while True:
        list_attendance_records(attendance_records)

        try:
            choice = input("Choose the index of an attendance record to modify: ")
            choice = int(choice)
            if choice <= 0 or len(attendance_records) < choice:
                raise ValueError()

            break
        except ValueError:
            print("Please enter an index from the list above.")

    chosen_record = attendance_records[choice - 1]

    return chosen_record


def prompt_user_for_attendance_option() -> thu.AttendanceOptions:
    while True:
        choice = input(
            "Would you like to mark the student as (p)resent, (e)xcused, or (a)bsent?"
        )
        if choice not in ["p", "e", "a", "present", "excused", "absent"]:
            print("Invalid choice. Try again.")
            continue

        break

    attendance_option = None

    if choice == "p" or choice == "present":
        attendance_option = thu.AttendanceOptions.PRESENT
    elif choice == "a" or choice == "absent":
        attendance_option = thu.AttendanceOptions.ABSENT
    else:
        attendance_option = thu.AttendanceOptions.EXCUSED

    return attendance_option


def main():
    auth_header = thu.get_auth_header_for_session()
    course = thu.prompt_user_for_th_course(auth_header)

    while True:
        student = thu.prompt_user_for_th_student(course, auth_header)

        while True:
            attendance_records = thu.get_attendance_records_for_student_in_course(
                course, student, auth_header
            )

            chosen_record = prompt_user_for_attendance_record_to_edit(
                attendance_records
            )
            new_attendance = prompt_user_for_attendance_option()

            thu.edit_attendance(
                course_id=course["course_id"],
                student_id=student["id"],
                attendance_id=chosen_record["id"],
                new_attendance=new_attendance,
                auth_header=auth_header,
            )

            print()
            keep_looping_records = input(
                f"Would you like to modify more attendance records for {student['name']}? (y/n): "
            )
            if keep_looping_records != "y":
                break

        print()
        keep_looping_students = input(
            f"Would you like to modify more attendance records for {course['course_name']}? (y/n): "
        )
        if keep_looping_students != "y":
            break

