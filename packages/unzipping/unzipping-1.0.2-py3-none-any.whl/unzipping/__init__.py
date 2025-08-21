"""The inverse of zip, including for empty iterables.

Functions
---------
unzip
    Unzip an iterable into a number of lists.
"""


def unzip(rows, column_count):
    """Unzip rows into column_count lists.

    >>> from unzipping import unzip
    >>> unzip([(8, 0), (7, 2), (9, 1)], 2)
    ([8, 7, 9], [0, 2, 1])
    >>> unzip([], 2)
    ([], [])
    """
    columns = tuple([] for _ in range(column_count))
    for row in rows:
        for column, element in zip(columns, row, strict=True):
            column.append(element)
    return columns
