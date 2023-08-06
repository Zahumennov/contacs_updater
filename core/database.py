import csv
import os

import psycopg2
from dotenv import load_dotenv

from core.defines import TABLE_NAME
from core.logger import logger
from core.utils import get_full_path

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
csv_path = get_full_path('../nimble_contacts.csv')


def execute_query(connection, query, values=None):
    """Execute a SQL query that modifies the database(INSERT, UPDATE, or DELETE statements).

    :param connection: An active database connection obtained from psycopg2.connect().
    :type connection: psycopg2.extensions.connection
    :param str query: The SQL query to be executed.
    :param list values: (Optional) List of values to be used as parameters in the query.
    """
    cursor = connection.cursor()
    cursor.execute(query, values)
    connection.commit()
    cursor.close()


def execute_select_query(connection, query, parameters=None):
    """Execute a SELECT SQL query and fetch the results.

    :param connection: An active database connection obtained from psycopg2.connect().
    :type connection: psycopg2.extensions.connection
    :param str query: The SQL query with placeholders to be executed.
    :param list parameters: (Optional) List of parameters to be substituted in the query placeholders.
    :return: The results of the SELECT query as a list of tuples.
    :rtype: list
    :raises psycopg2.DatabaseError: If an error occurs during query execution.
    """
    try:
        cursor = connection.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("Сталася помилка:", error)
        return None


def create_connection(dbname=None):
    """Create a connection to the PostgreSQL database.

    :param str dbname: (Optional) The name of the database to connect to.
    :return: A connection object to the PostgreSQL database.
    :rtype: psycopg2.extensions.connection
    :raises psycopg2.Error: If there is an error creating the database connection.
    """
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME") if not dbname else dbname,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


def check_database_exists():
    """Check if the PostgreSQL database exists.

    :return: True if the database exists, False otherwise.
    :rtype: bool
    """
    try:
        connection = create_connection()
        connection.close()
        return True
    except psycopg2.OperationalError:
        return False


def create_database():
    """Create the PostgreSQL database.

    :raises psycopg2.Error: If there is an error creating the database.
    """
    try:
        connection = create_connection(dbname='postgres')
        connection.autocommit = True

        execute_query(connection, f"CREATE DATABASE {DB_NAME};")
        logger.info(f"База даних '{DB_NAME}' успішно створена!")

        connection.close()

    except psycopg2.Error as e:
        logger.error("Помилка при створенні бази даних: %s", e)


def create_table():
    """Create the 'contacts' table in the PostgreSQL database with columns for 'id', 'first_name', 'last_name', and
    'email'.

    :raises psycopg2.Error: If there is an error creating the table.
    """
    try:
        with create_connection() as connection:
            create_table_query = f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                email VARCHAR(100)
            );
            '''
            execute_query(connection, create_table_query)
            logger.info("Таблиця успішно створена!")

    except psycopg2.Error as e:
        logger.error("Помилка при створенні таблиці:", e)


def is_table_empty():
    """Check if the 'contacts' table is empty in the PostgreSQL database.

    :return: True if the 'contacts' table is empty, False otherwise.
    :rtype: bool
    :raises psycopg2.Error: If there is an error executing the query.
    """
    with create_connection() as connection:
        if not execute_select_query(connection, f"SELECT * FROM {TABLE_NAME} LIMIT 1"):
            return True
        return False


def init_table():
    """Initialize the 'contacts' table with data from a CSV file.

    :raises FileNotFoundError: If the CSV file specified by 'csv_path' is not found.
    :raises psycopg2.Error: If there is an error executing the insert queries.
    """
    if not is_table_empty():
        return
    with create_connection() as connection, open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)
        for row in csv_reader:
            sql_query = f"INSERT INTO {TABLE_NAME} (first_name, last_name, email) VALUES (%s, %s, %s)"
            values = (row[0], row[1], row[2])
            execute_query(connection, sql_query, values)
    logger.info("Таблиця успішно ініціалізована!")


def is_index_exists():
    """Check if the 'contacts_search_idx' index exists in the 'contacts' table.

    :return: True if the 'contacts_search_idx' index exists, False otherwise.
    :rtype: bool
    :raises psycopg2.Error: If there is an error executing the query.
    """
    try:
        with create_connection() as connection:
            search_query = f"""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'contacts'
                AND indexname = 'contacts_search_idx';
            """

            if execute_select_query(connection, search_query):
                return True
            return False
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("Помилка при перевірці індексу:", error)


def create_search_index():
    """Create the 'contacts_search_idx' index for full-text search.

    :raises psycopg2.Error: If there is an error creating the index.
    """
    if is_index_exists():
        return
    try:
        with create_connection() as connection:
            create_index_query = f"""
                CREATE INDEX contacts_search_idx 
                ON {TABLE_NAME} USING GIN (to_tsvector('english', first_name || ' ' || last_name || ' ' || email));
            """
            execute_query(connection, create_index_query)
            logger.info("Індекс повнотекстового пошуку створено успішно.")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("Помилка при створенні індексу:", error)
