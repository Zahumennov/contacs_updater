from fastapi import FastAPI, HTTPException, Query
from starlette import status

from core.database import execute_select_query, create_connection
from core.utils import prepare_data

app = FastAPI()


@app.get("/contacts/", status_code=status.HTTP_200_OK)
def get_contacts_by_full_text(keyword: str = Query(..., min_length=1)):
    """View for searching contacts by full text. This endpoint allows searching contacts based on a given keyword that
    must have a minimum length of 1 character.

    :param str keyword: The search keyword used to find contacts in the database.
    :return: A dictionary containing the search results.
    :rtype: dict
    :raises HTTPException 500: If there is an error executing the search.
    """
    try:
        with create_connection() as connection:
            parameters = (keyword,)
            search_query = f"""
                SELECT *
                FROM contacts
                WHERE to_tsvector('english', first_name || ' ' || last_name || ' ' || email) 
                @@ to_tsquery('english', %s);
            """
            search_results = execute_select_query(connection, search_query, parameters)
            data = prepare_data(search_results)
            return {"results": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Помилка при виконанні пошуку")


@app.get("/docs", include_in_schema=False)
async def get_docs():
    """Get API documentation. This function allows fetching the API documentation in the OpenAPI JSON format.

    :return: The API documentation object in OpenAPI JSON format.
    :rtype: dict
    """
    with open('docs/openapi.json') as f:
        return eval(f.read())
