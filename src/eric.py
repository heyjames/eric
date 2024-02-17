import api
from config_module import config
from datetime import datetime
import schedule
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

# Perform cleanup on system exit
def cleanup_before_exit():
    print("Performing cleanup...")

    sys.exit(0)

# Register times in the scheduler module
def setup_scheduler():
    if config['settings'].getboolean('debug'):
        # schedule.every().sunday.at('01:26').do(task)
        schedule.every(1).seconds.do(task)
    else:
        # Get schedule from config file
        for day, times_str in config['schedule'].items():
            # Split the comma-separated times
            times = []
            for time in times_str.split(','):
                stripped_time = time.strip()
                times.append(stripped_time)

            # Parse and schedule jobs for each time in the list
            for time_str in times:
                parsed_time = datetime.strptime(time_str, '%H:%M').time()
                print(f"::: parsed_time.strftime('%H:%M') ::: {day} {parsed_time.strftime('%H:%M')}")
                getattr(schedule.every(), day).at(parsed_time.strftime('%H:%M')).do(task)

# Tasks executed by the scheduler module
def task():
    print('job() function executed.')

    # Format meeting data into dictionaries from Legistar website
    upcoming_meetings, all_meetings = api.get_formatted_upcoming_and_all_meetings()

    # Get the first non-canceled meeting
    first_non_canceled_meeting =  api.get_first_non_canceled_meeting(upcoming_meetings)

    # Get the Zoom registration link from the PDF and check its HTTP response
    if config['settings'].getboolean('debug'):
        # pdf_path = config['settings']['debug_pdf_url']
        pdf_path = config['settings']['debug_pdf_path']
        pdf_data = api.get_pdf_data(pdf_path)
    else:
        pdf_data = api.get_pdf_data(first_non_canceled_meeting['agenda'])

    # Combine the meeting data with the PDF data into one dictionary
    result = api.combine_pdf_and_meeting_data(first_non_canceled_meeting, pdf_data)

    print(result)

    # Send an email about broken Zoom links to recipients listed in the 
    # config.cfg file
    if not result['is_valid_zoom_registration_link'] and config['settings'].getboolean('enable_email_notifications'):
        try:
            api.send_emails(result)
        except Exception as e:
            print(f'Error sending email: {e}')

# Begin script
if __name__ == "__main__":
    # Register the default SIGINT handler (^C will terminate the script)
    signal.signal(signal.SIGINT, signal.default_int_handler)

    try:
        setup_scheduler()
        main_loop()
    except KeyboardInterrupt:
        # Executed when ^C is pressed
        print("\n^C detected. Exiting gracefully...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Executed on script exit (normal or exception)
        print("Script exiting.")