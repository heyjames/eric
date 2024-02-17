from config_module import config
from datetime import datetime
import schedule

# Register times in the scheduler module
def setup_scheduler(callback):
    if config['settings'].getboolean('debug'):
        # schedule.every().sunday.at('01:26').do(task)
        schedule.every(1).seconds.do(callback)
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
                getattr(schedule.every(), day).at(parsed_time.strftime('%H:%M')).do(callback)