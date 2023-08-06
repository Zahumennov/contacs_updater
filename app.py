import uvicorn

from core.database import check_database_exists, DB_NAME, create_database, create_table, init_table, create_search_index
from core.logger import logger
from core.views import app

if __name__ == "__main__":
    if check_database_exists():
        logger.info(f"База даних '{DB_NAME}' вже існує.")
    else:
        create_database()
    create_table()
    init_table()
    create_search_index()
    uvicorn.run(app)


