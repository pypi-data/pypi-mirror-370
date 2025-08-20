from itertools import chain


def unnested_list(value):
    """Unnested List Filter template function."""
    return (
        list(chain.from_iterable(value))
        if value != []
        else ["no_back_fill_blob"]
    )
