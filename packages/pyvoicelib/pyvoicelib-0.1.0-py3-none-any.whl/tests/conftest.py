import warnings

def pytest_configure():
    """Ignore noisy DeprecationWarnings from speech_recognition"""
    warnings.filterwarnings(
        "ignore", 
        category=DeprecationWarning, 
        module="speech_recognition"
    )
