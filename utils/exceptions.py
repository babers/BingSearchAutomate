# utils/exceptions.py - Custom exceptions

class BrowserControllerException(Exception):
    """Exception raised by the browser controller."""
    pass

class ConfigurationException(Exception):
    """Exception raised during configuration loading."""
    pass

class DataManagerException(Exception):
    """Exception raised by the data manager."""
    pass
