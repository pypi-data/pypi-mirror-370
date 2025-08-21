from .mwc_backend import MWCBackend

def get_backend(name):
    return {
        'mwc': MWCBackend,
    }[name]
