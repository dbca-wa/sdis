import signals  # NOQA

VERSION = (3, 0, 0, 'alpha', 0)


def get_version(*args, **kwargs):
    # Don't litter pythia/__init__.py with all the get_version stuff.
    # Only import if it's actually called.
    from pythia.utils import get_version
    return get_version(*args, **kwargs)
