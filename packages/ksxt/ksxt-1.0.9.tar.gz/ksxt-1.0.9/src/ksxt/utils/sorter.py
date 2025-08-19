import collections


@staticmethod
def sort_by(array, key, descending=False):
    return sorted(
        array, key=lambda k: getattr(k, key, None) if getattr(k, key, None) is not None else "", reverse=descending
    )
