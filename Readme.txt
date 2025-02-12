
Setup Virtual Environment for Django - Visual Studio Code

- Download & Installation der aktuellen Python Version: https://www.python.org/downloads/

- Softwareprojekt in Visual Studio Code öffnen

- Ordner mit der manage.py öffnen und dort neues Terminal starten, je nach OS folgende Befehle ausführen

# Linux
sudo apt-get install python3-venv    # If needed
python3 -m venv .venv
source .venv/bin/activate

# macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
py -3 -m venv .venv
.venv\scripts\activate


- Command Palette öffnen ( Ctrl+Shift+P ) --> Python: Select Interpreter 
- Von der Liste der Interpreter die Virtual Environment auswählen: sollte mit ./.venv oder .\.venv beginnen.

- Neues Terminal starten --> darauf achten das Virtual Environment aktiv ist
- Folgende Befehle ausführen:

python -m pip install --upgrade pip
python -m pip install django
python -m pip install django 


Einrichtung sollte damit abgeschlossen sein und das Django Project kann mit folgendem Befehl ausgeführt werden:
python manage.py runserver



Eine ausführliche Beschreibung gibt es auf folgender Seite:
https://code.visualstudio.com/docs/python/tutorial-django
