class ApplicationException(Exception):
    def __init__(self,message):
        super().__init__("Request error: " + message + ".\nError ID:{error.id}")