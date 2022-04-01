from typing import Mapping


def is_safe_action(action):
    return action.upper() in ["GET"]


def get_attribute(instance, attrs):
    for attr in attrs:
        try:
            if isinstance(instance, Mapping):
                instance = instance[attr]
            elif isinstance(instance, list):
                instance = instance[int(attr)]
            else:
                instance = getattr(instance, attr)
        except (KeyError, TypeError, Exception):
            return None
    return instance
