# ewha-db-dynamicP

A Python package for managing PostgreSQL database connections and processing trajectory data collected from CCTV systems.


## How to use

'''python
from ewha_db_manager.db_manager import DBManager

db = DBManager(
    host = "localhost",
    port = your port number,
    dbname = "your_database",
    user = "your_username",
    password = "your_password"
)

df_group = db.dataframe_groups("your_table")
'''

db.dataframe_groups automatically fetches data from a PostgreSQL database, processes it into trajectory datasets, and groups the results by the CCTV ID where each trajectory was recorded.

## Requirements

psycopg2-binary
pandas
geopandas
movingpandas
tqdm
pyyaml

## License
This project is licensed under the JiyoonLee License.

## Contact
0197black@gmail.com
