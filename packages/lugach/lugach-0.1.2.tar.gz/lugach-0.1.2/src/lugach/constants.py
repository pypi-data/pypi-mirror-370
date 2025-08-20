def _get_grade_ranges():
    sorted_cutoffs = sorted(
        _GRADE_CUTOFFS.items(), key=lambda item: item[1], reverse=True
    )
    adjusted_cutoffs = [
        (grade, cutoff - _FINAL_GRADE_TOLERANCE) for grade, cutoff in sorted_cutoffs
    ]

    grade_ranges = []
    for i, (grade, cutoff) in enumerate(adjusted_cutoffs):
        lower_bound = cutoff
        upper_bound = adjusted_cutoffs[i - 1][1] if i > 0 else 1000

        grade_ranges.append((grade, range(lower_bound, upper_bound)))

    return grade_ranges


GLOBAL_TIMEOUT_SECS = 5
RELOAD_ATTEMPTS = 10
CHUNK_SIZE = 20

QUIZ_CONCERN_TOLERANCE = 2
QUIZ_CONCERN_SUBJECT = "Quiz concern - {course_name}"
QUIZ_CONCERN_BODY = """Hello, I've noticed that you've missed multiple quizzes this semester. Make sure to keep up with the class announcements and modules in Canvas. There are two extra credit opportunities that can help you make up the points missed due at the end of the semester.

"Let me know if you have any questions!
{instructor_name}"""

_FINAL_GRADE_TOLERANCE = 10
_GRADE_CUTOFFS = {
    "A": 900,
    "B": 800,
    "C": 700,
    "D": 600,
}
GRADE_RANGES = _get_grade_ranges()
