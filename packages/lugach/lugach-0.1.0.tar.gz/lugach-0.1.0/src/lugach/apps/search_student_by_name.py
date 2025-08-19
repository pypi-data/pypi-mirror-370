import lugach.cvutils as cvu

from canvasapi.exceptions import BadRequest
from itertools import chain


def print_selected_courses(selected_courses):
    for i, (course, selected) in enumerate(selected_courses.items()):
        indicator = "*" if selected else " "
        print(f"{indicator} {i + 1}. {cvu.course_name_with_date(course)}")


def confirm_courses_to_search(selected_courses):
    while True:
        print_selected_courses(selected_courses)

        while True:
            try:
                user_selection = input(
                    "Choose the courses to search by index (or 'q' to quit): "
                )
                if user_selection == "q":
                    return selected_courses

                selected_course_index = int(user_selection) - 1
                if not (0 <= selected_course_index < len(selected_courses)):
                    raise ValueError

                break
            except ValueError:
                print("Expected 'q' or an index within range. Try again.")

        selected_course = list(selected_courses)[selected_course_index]
        selected_courses[selected_course] = not selected_courses[selected_course]


def take_student_query(sources):
    while True:
        try:
            query = input("Search for the student by name: ")
            sources = [cvu.filter_users_by_query(source, query) for source in sources]
            return sources
        except BadRequest as e:
            cvu.process_bad_request(e)


def main():
    canvas = cvu.create_canvas_object()
    courses = cvu.get_courses_from_canvas_object(canvas)

    init_courses = {course: False for course in courses if course.start_at}
    selected_courses_dict = confirm_courses_to_search(init_courses)
    selected_courses = [
        course
        for course in selected_courses_dict.keys()
        if selected_courses_dict[course]
    ]

    while True:
        sources = selected_courses
        while True:
            sources = take_student_query(sources)

            flattened_source = list(chain(*sources))
            number_of_students = len(flattened_source)

            if number_of_students == 0:
                print()
                print("No such student was found.")
                print()
                sources = selected_courses
                continue
            elif number_of_students == 1:
                student = flattened_source[0]
                print()
                print(f"You selected {student.name}.")
                break

            print()
            print(f"Your query returned {number_of_students} students.")
            print("Here are their names:\n")
            for i, source in enumerate(sources):
                for student in source:
                    course = selected_courses[i]
                    print(f"    {student.name:25} ({course.name})")
            print()

        name = student.name
        index_of_course = sources.index([student])
        course = selected_courses[index_of_course]
        email = student.email

        print()
        print(f"Name: {name}")
        print(f"Course: {course.name}")
        print(f"Email: {email}")
        print()

        keep_looping = input(
            "Would you like to keep looking for students in these courses? (y/n): "
        )
        if cvu.sanitize_string(keep_looping) != "y":
            break

