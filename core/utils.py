import os


def get_full_path(filename):
    """Get the full path to a file in the current directory.

    :param str filename: The name of the file for which the full path is required.
    :return: The full path to the specified file.
    :rtype: str
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, filename)


def prepare_data(data):
    """Prepare the search results data for the response.

    :param list data: The list of tuples containing search results from the 'contacts' table.
    :return: A list of dictionaries containing the prepared data for each search result.
    :rtype: list
    """
    if not data:
        return data
    prepared_data = []
    for item in data:
        prepared_data.append({
            'id': item[0],
            'first_name': item[1],
            'last_name': item[2],
            'email': item[3]
        })
    return prepared_data
