import os

DEFAULT_DATA_DIR = "~/.anges/data/event_streams"

def get_data_dir():
    """Get the current data directory, allowing for runtime override"""
    data_dir = os.getenv('ANGES_EVENT_STREAM_DATA_DIR', DEFAULT_DATA_DIR)
    return os.path.expanduser(data_dir)

DATA_DIR = get_data_dir()