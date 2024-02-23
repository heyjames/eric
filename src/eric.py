import api
from config import config
import schedule
from task_scheduler import setup_scheduler
import signal
import time
import utils

# TODO
# Add validation to dictionaries (e.g., legistar_parser.py get_data())
# Add log handlers
# Add bubble up error handling and add to log file
# Handle first time debug mode missing files

# Main loop
def main_loop():
    print("Press ^C to exit gracefully.")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)

        except Exception as e:
            print(str(e))

# Tasks executed by the scheduler module
def task():
    print(f'\n::: {utils.get_readable_date_time()} ::: START task()\n')

    # Get data from Legistar's calendar
    # first_legistar_meeting = api.get_first_legistar_meeting()
    # print(first_legistar_meeting)
    # print(f'\n\n               eric.py - task() - spacer\n\n')

    # Get data from NovusAgenda's calendar
    first_novus_meeting = api.get_first_novus_meeting()
    print(first_novus_meeting)
    print(f'\n\n               eric.py - task() - spacer\n\n')

    # Send an email to recipients listed in the config.cfg file if broken Zoom 
    # links are detected
    # if config['settings'].getboolean('enable_email_notifications'):
        # try:
            # api.send_emails(first_legistar_meeting_data)
        # except Exception as e:
            # print(f'Error sending email: {e}')

    print(f'\n::: {utils.get_readable_date_time()} ::: END task()\n')

# Begin script
if __name__ == "__main__":
    try:
        # Register the default SIGINT handler (^C will terminate the script)
        signal.signal(signal.SIGINT, signal.default_int_handler)

        # Register the task() function as a callback
        setup_scheduler(task)

        main_loop()
    except KeyboardInterrupt:
        # Executed when ^C is pressed
        print("\n^C detected. Exiting gracefully...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Executed on script exit (normal or exception)
        print("Script exiting.")