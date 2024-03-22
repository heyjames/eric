A server application designed to enhance the Legistar website experience.
* Configure a schedule to periodically validate the next meeting's Zoom registration link inside of the PDF
* Interface with the browser script to highlight canceled meetings, empty meeting entries
* Validate Zoom registration links for School Board's agenda

Future capabilities
* Detect when a member will be attending the meeting remotely in the agenda PDF
* Detect and extract the closed session time from the agenda PDF

## Install Virtual Environment
```
cd eric
python3 -m venv ./venv
```

## Activate Virtual Environment
```
cd eric
source venv/bin/activate
```

## Install Dependencies
```
cd eric
pip install -r requirements.txt
```

## Configure Email Notifications
1. Create a new project at ```https://console.cloud.google.com/```
2. Create a new credential OAuth Client ID
3. Download .json file to the root folder of the project and rename it to ```client_secret.json```

## Configuration
#### Confirm schedule
Edit the day and time in ```src/config.cfg```.

## Start Script
```
cd eric/src
python3 eric.py
```


## Topology

                        (main loop, init)
                         =============                
                        |             |                                    
                        |   eric.py   |                                    
                        |             |
                         ==============                      
                                ^                             
                                |                             
                                v                             
     ========================================================== 
    |                                                          |
    |                           api.py                         |
    |                                                          |
     ========================================================== 
        ^                                         ^                     
        |                                         |                     
        |                                         |                     
        v (I/O layer)                             v (OS control/tools)  
     ========================           ======================= 
    |                        |         |                       |
    |   legistar_parser.py   |         |   task_scheduler.py   |
    |                        | <-----> |                       |
    |   novus_parser.py      |         |   utils.py            |
    |                        |         |                       |
    |   pdf_parser.py        |         |   gmail.py            |
    |                        |         |                       |
     ========================          |   log.py              |
                                       |                       |
                                       |                       |
                                        ======================= 
