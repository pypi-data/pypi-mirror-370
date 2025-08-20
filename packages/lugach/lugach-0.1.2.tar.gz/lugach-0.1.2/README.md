# LUGACH

LU GA Canvas Helps (or LUGACH for short) is a Python application that provides
a number of utilities designed to make daily tasks more efficient for GAs at
Liberty University.

It synchronizes across Canvas, Top Hat, and Lighthouse to automate tasks such
as confirming student enrollment, retrieving emails, modifying due dates/time
limits on quizzes/assignments, and more.

## Requirements

The project currently requires Python 3.12.0. See below for installation
instructions for typical users and for developers/contributors.

It's also helpful to have Git installed on your machine if you plan to
contribute to development.

## Installation

### For Typical Users

The easiest way to install and run LUGACH is with
[pipx](https://pypa.github.io/pipx/), which will install the tool in an
isolated environment and make the `lugach` command available globally:

```bash
pipx install lugach
```

After installation, you can run the project from anywhere using the CLI
command:

```bash
lugach
```

### For Developers/Contributors

First, use git to clone the project to a local folder:

```bash
git clone https://github.com/dnicholson314/LU-GA-Canvas-Helps.git
cd LU-GA-Canvas-Helps
```

Next, install the dependencies and the CLI in editable mode using
[uv](https://github.com/astral-sh/uv):

```bash
uv tool install . -e
```

You can now run the project using:

```bash
lugach
```

## Usage

**The first time you run the project, you should open the Setup application**:

```txt
    Welcome to LUGACH! Please choose one of the following options
(or 'q' to quit): 
        (1) Setup **this option here**
        (2) Identify Absent Students
        (3) Identify Quiz Concerns
        (4) Modify Due Dates
        (5) Modify Time Limits
        (6) Post Final Grades
        (7) Search Student By Name
        (8) Update Attendance Verification
        (9) Modify Attendance
```

That application will let you add the various authentication details you need
for various aspects of the project.
