import api
import color
from config import config
from log import logger
import schedule
from task_scheduler import setup_scheduler
import signal
import sys
import time
import traceback
import utils

# TODO
# Handle first time debug mode missing files
# Allow notifications for canceled meetings - store previous state in a database?

# Main loop
def main_loop():
    logger.info('Starting main_loop')
    print(color.BLUE + 'Press ^C to exit gracefully.' + color.RESET)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
            # raise ValueError('This is a custom error message')

        except Exception as e:
            print(color.RED + 'A critical error has occurred in the main loop:\n' + str(e) + color.RESET)
            logger.critical('A critical error has occurred in the main loop: ' + str(e))
            break

# Tasks executed by the scheduler module
def task():
    print(f'\n::: {utils.get_readable_date_time()} ::: START task()\n')
    logger.info('Starting task')

    # Get data from Legistar's calendar
    logger.debug('Getting first Legistar meeting')
    first_legistar_meeting = api.get_first_legistar_meeting()
    print(f'\n{first_legistar_meeting}')

    # Get data from NovusAgenda's calendar
    logger.debug('Getting first Novus meeting')
    first_novus_meeting = api.get_first_novus_meeting()
    print(f'\n{first_novus_meeting}')

    # Send an email to recipients listed in the config.cfg file if broken Zoom 
    # links are detected
    # if config['settings'].getboolean('enable_email_notifications'):
        # try:
            # api.send_emails(first_legistar_meeting_data)
        # except Exception as e:
            # print(f'Error sending email: {e}')

    print(f'\n\n::: {utils.get_readable_date_time()} ::: END task()\n')

    # Exit out of the script after running the task once when debugging
    if config['developer'].getboolean('debug_enable'):
        sys.exit(0)

# Begin script
if __name__ == "__main__":
    try:
        logger.info('Starting eric.py')
        # Register the default SIGINT handler (^C will terminate the script)
        signal.signal(signal.SIGINT, signal.default_int_handler)

        # Register the task() function as a callback
        setup_scheduler(task)

        main_loop()
    except KeyboardInterrupt:
        # Executed when ^C is pressed
        print('\n\n' + color.BLUE + '^C detected. Exiting.' + color.RESET)
        logger.info('^C detected')
    except Exception as e:
        print(traceback.format_exc())
    finally:
        # Executed on script exit (normal or exception)
        print(color.BLUE + 'Exiting.' + color.RESET)
        logger.info('Exiting program')