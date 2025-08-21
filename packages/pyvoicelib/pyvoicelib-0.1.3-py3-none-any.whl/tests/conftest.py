import warnings

def pytest_configure():
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="speech_recognition")
    warnings.filterwarnings("ignore", category=UserWarning, module="pyvoicelib.core")
