import os

import requests
from dotenv import load_dotenv

from core.database import create_connection, execute_query, execute_select_query
from core.defines import NimbleContact, TABLE_NAME
from core.logger import logger
from tasks.task_manager import celery_app

load_dotenv()


def get_data():
    """Retrieve data from the Nimble API.

    :return: The JSON data containing contact information retrieved from the Nimble API.
    :rtype: dict
    :raises requests.exceptions.RequestException: If there is an error making the API request.
    """
    headers = {
        "Authorization": f"Bearer {os.getenv('NIMBLE_API_TOKEN')}"
    }
    params = {
        "fields": "first name,last name,email",
        "record_type": "person"
    }
    try:
        response = requests.get(os.getenv('NIMBLE_API_URL'), headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data
        logger.error(f"Помилка запиту: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Помилка при з'єднанні: {e}")


def parse_data(data):
    """Parse data from the Nimble API response.

    :param dict data: The JSON data retrieved from the Nimble API response.
    :return: A list of NimbleContact objects containing the parsed contact information.
    :rtype: list
    """
    parsed_data = []
    for item in data['resources']:
        fields = item['fields']
        first_name = fields.get('first name', [{}])[0].get('value')
        last_name = fields.get('last name', [{}])[0].get('value')
        email = fields.get('email', [{}])[0].get('value')

        parsed_data.append(
            NimbleContact(
                first_name=first_name,
                last_name=last_name,
                email=email
            )
        )
    return parsed_data


def is_record_exists(connection, item):
    """Check if a contact record already exists in the 'contacts' table.

    :param connection: An active database connection obtained from psycopg2.connect().
    :type connection: psycopg2.extensions.connection
    :param NimbleContact item: The NimbleContact object representing the contact to check for existence.
    :return: True if the contact record exists, False otherwise.
    :rtype: bool
    :raises psycopg2.Error: If there is an error executing the query.
    """
    first_name = f"first_name = '{item.first_name}'" if item.first_name else "first_name IS NULL"
    last_name = f"last_name = '{item.last_name}'" if item.last_name else "last_name IS NULL"
    email = f"email = '{item.email}'" if item.email else "email IS NULL"
    select_query = f"SELECT * FROM {TABLE_NAME} WHERE {first_name} AND {last_name} AND {email};"
    if execute_select_query(connection, select_query):
        return True
    return False


def update_data(parsed_data):
    """Update the 'contacts' table with the parsed data.

    :param list parsed_data: A list of NimbleContact objects containing the parsed contact information.
    :raises psycopg2.Error: If there is an error executing the insert query.
    """
    with create_connection() as connection:
        for item in parsed_data:
            if is_record_exists(connection, item):
                continue
            insert_query = f"INSERT INTO {TABLE_NAME} (first_name, last_name, email) VALUES (%s, %s, %s)"
            values = (item.first_name, item.last_name, item.email)
            execute_query(connection, insert_query, values)
        logger.info("Таблиця успішно оновлена!")


@celery_app.task
def run_worker():
    """ This function is task of `celery` queue. It performs monitoring of services expiration."""
    if not (data := get_data()):
        return
    if not (parsed_data := parse_data(data)):
        return
    update_data(parsed_data)


if __name__ == '__main__':
    run_worker()
