import lugach.cvutils as cvu
import lugach.thutils as thu
import lugach.lhutils as lhu

WELCOME_MESSAGE = """\
    Welcome to LUGACH! This application will walk you through the steps
    necessary to connect Canvas and Lighthouse to LUGACH and get the
    program running as intended.

    Press ENTER to continue or (q) to quit. \
"""

CANVAS_MESSAGE = """\
    First, we'll check to see if you created an .env file and added
    your Canvas API key. If not, we'll go ahead and do those things.\
"""

TOP_HAT_MESSAGE = """\
    Next, we'll go ahead and set up your Top Hat credentials. This
    will require obtaining your JWT refresh key from Top Hat. Would
    you like to do this now (y/n)? \
"""

LIGHTHOUSE_MESSAGE = """\
    Almost done! The last thing we'll do is update your Liberty
    credentials for Lighthouse. Would you like to do this now (y/n)? \
"""

SETUP_COMPLETE = """\
    You're all done with setup!

    Press ENTER to quit.
"""


def main():
    continue_setup = input(WELCOME_MESSAGE)
    if continue_setup == "q":
        return

    print()
    print(CANVAS_MESSAGE)
    print()

    cvu.create_canvas_object()

    print()
    th_setup = input(TOP_HAT_MESSAGE)
    print()

    if th_setup == "y":
        thu.update_env_file_with_th_auth_token()

    print()
    lh_setup = input(LIGHTHOUSE_MESSAGE)
    print()

    if lh_setup == "y":
        lhu.prompt_user_for_liberty_credentials()

    print()
    input(SETUP_COMPLETE)

