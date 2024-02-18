import api
from config_module import config
import schedule
from task_scheduler import setup_scheduler
import signal
import sys
import time

# TODO
# Add validation to dictionaries (e.g., legistar_parser.py get_data())
# Add log handlers
# Add bubble up error handling and add to log file

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
    print('job() function executed.')

    # Get data from NovusAgenda's calendar
    first_novus_meeting_data = api.get_first_novus_meeting_data()
    print(first_novus_meeting_data)

    # Get data from Legistar's calendar
    # first_legistar_meeting_data = api.get_first_meeting_data()
    # print(first_legistar_meeting_data)

    # # Send an email about broken Zoom links to recipients listed in the 
    # # config.cfg file
    # if not first_legistar_meeting_data['is_valid_zoom_registration_link'] and config['settings'].getboolean('enable_email_notifications'):
    #     try:
    #         api.send_emails(first_legistar_meeting_data)
    #     except Exception as e:
    #         print(f'Error sending email: {e}')

# Begin script
if __name__ == "__main__":
    # Register the default SIGINT handler (^C will terminate the script)
    signal.signal(signal.SIGINT, signal.default_int_handler)

    try:
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