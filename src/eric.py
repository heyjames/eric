import api
from config_module import config
from datetime import datetime
import schedule
import signal
import sys
import time

# TODO
# Add validation to dictionaries (e.g., legistar_parser.py get_data())
# Add a log handler
# Add bubble up error handling and add to log file
# Extract CSS selectors to config file

# api.py
    # get_first_non_canceled_meeting(meetings)
        # Handle whether the argument is from the Upcoming or All Meetings section. 
        # All Meetings might require a descending loop.

    # get_formatted_upcoming_and_all_meetings()

# legistar_parser.py
    # download_html_response()
        # Test a non-yes answer

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
    # Used for testing
    # schedule.every().sunday.at('01:26').do(task)
    # schedule.every(1).seconds.do(task)

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
            print("::: parsed_time.strftime('%H:%M') :::", parsed_time.strftime('%H:%M'))
            getattr(schedule.every(), day).at(parsed_time.strftime('%H:%M')).do(task)

# Tasks executed by the scheduler module
def task():
    print('job() function executed.')

    # Format meeting data into dictionaries from Legistar website
    upcoming_meetings, all_meetings = api.get_formatted_upcoming_and_all_meetings()

    # Get the first non-canceled meeting
    first_non_canceled_meeting =  api.get_first_non_canceled_meeting(upcoming_meetings)

    # Get the Zoom registration link from the PDF and check its HTTP response
    # pdf_path = 'https://alameda.legistar.com/View.ashx?M=A&ID=1157953&GUID=5BF30CE1-10BE-4DEF-81ED-FFDA441F484E'
    # pdf_path = '/Users/james/Downloads/agenda_broken_link.pdf' # Development
    # pdf_data = api.get_pdf_data(pdf_path) # Development
    pdf_data = api.get_pdf_data(first_non_canceled_meeting['agenda'])

    # Combine the meeting data with the PDF data into one dictionary
    result = api.combine_pdf_and_meeting_data(first_non_canceled_meeting, pdf_data)

    print(result)

# Begin script
if __name__ == "__main__":
    # Register the default SIGINT handler (^C will terminate the script)
    signal.signal(signal.SIGINT, signal.default_int_handler)

    setup_scheduler()

    try:
        main_loop()

    except KeyboardInterrupt:
        # Executed when ^C is pressed
        print("\n^C detected. Exiting gracefully...")

    finally:
        # Executed on script exit (normal or exception)
        print("Script exiting.")