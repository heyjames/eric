A server application designed to enhance the Legistar website experience.
* Validate Zoom registration links in PDFs
* Interface with the browser script to highlight canceled meetings, empty meeting entries

## Install Virtual Environment
```
cd eric
python3 -m venv ./venv
source venv/bin/activate
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

## Configuration
#### Confirm schedule
Edit the day and time in ```src/config.cfg```.

## Start Script
```
cd eric/src
python3 eric.py
```