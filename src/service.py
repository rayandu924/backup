import win32serviceutil
import win32service
import win32event
import servicemanager
import os
import sys
import time
from dotenv import load_dotenv

class FlaskService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FlaskBackupService"
    _svc_display_name_ = "Flask Backup Service"
    _svc_description_ = "This service runs a Flask application for backup."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ""))
        self.start_flask_app()

    def start_flask_app(self):
        # Charger l'environnement
        load_dotenv(dotenv_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), '../.env'))
        
        # Importer le serveur Flask
        from app import app  # Remplacer par le nom du fichier de l'application
        
        # Démarrer l'application Flask
        app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(FlaskService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(FlaskService)

#CHANGER DE PYTHON NE PAS PRENDRE LE WINDOWS STORE MAIS LE PYTHON CLASSIQUE POUR INSTAL SERVICE 