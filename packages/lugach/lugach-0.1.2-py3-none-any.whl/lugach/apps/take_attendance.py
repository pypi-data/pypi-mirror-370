import lugach.thutils as thu


def main():
    auth_header = thu.get_auth_header_for_session()

    course = thu.prompt_user_for_th_course(auth_header)
    course_id = course["course_id"]

    attendance_item, _ = thu.create_attendance(auth_header, course_id)
    attendance_item_id = attendance_item["id"]

    while True:
        attended_students, total_students = thu.monitor_attendance(
            auth_header, course_id, attendance_item_id
        )

        print()
        print(f"Attendance: {attended_students}/{total_students}")
        continue_monitoring = input("Press ENTER to refresh or q to quit monitoring. ")

        if continue_monitoring == "q":
            break

    print()
    prompt_to_close = input("Would you like to close attendance? (y/n) ")
    if prompt_to_close != "y":
        return

    thu.close_attendance(auth_header, course_id, attendance_item_id)
