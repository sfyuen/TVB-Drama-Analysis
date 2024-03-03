import json
import pandas as pd
from neo4j import GraphDatabase

#URI = "<URI for Neo4j database>"
#AUTH = ("<Username>", "<Password>")

#Connection URI for the neo4j instance
URI = ""
#Login credentials for the neo4j instance (username,password)
AUTH = ("", "")
#Name of database to load the data
db = ""

driver = GraphDatabase.driver(URI, auth=AUTH)

# path to df_details.json
df_details=pd.read_json("df_details.json")
for index, row in df_details.iterrows():
    driver.execute_query(
        "CREATE (:Drama {name: $name, id: $id, episodes: $eps, production_start: $prod_start, production_end: $prod_end})",
        name = row['name'],
        id = index,
        eps = row['eps'],
        prod_start = row['prod_start'],
        prod_end = row['prod_end'],
        database_=db,
    )
print('Loaded drama nodes')

# path to df_sub_category.json
df_genre=pd.read_json("df_sub_category.json")
for index, row in df_genre.iterrows():
    driver.execute_query(
        """MATCH (d:Drama {id: $id}) 
        MERGE (g:Genre {name: $genre})
        CREATE (d)-[r:HAS_GENRE]->(g)
        """,
        id = row['id'],
        genre = row['sub_category'],
        database_=db,
    )
print('Loaded genre nodes')

# path to df_crew.json
df_crew=pd.read_json("df_crew.json")
for index, row in df_crew.iterrows():
    driver.execute_query(
        """MATCH (d:Drama {id: $id}) 
        MERGE (p:Person {name: $name})
        CREATE (p)-[r:"""+"IS_"+row['post'].upper()+"_OF"+"]->(d)",
        id = row['id'],
        name = row['name'],
        database_=db,
    )
print('Loaded crew nodes')

# path to df_cast.json
df_cast=pd.read_json("df_cast.json")
for index, row in df_cast.iterrows():
    if not row['role']:
        driver.execute_query(
            """MATCH (d:Drama {id: $id}) 
            MERGE (p:Person {name: $name})
            CREATE (p)-[r:ACTED_IN]->(d)""",
            id=row['id'],
            name=row['actor'],
            database_=db,
        )
    else:
        driver.execute_query(
            """MATCH (d:Drama {id: $id}) 
            MERGE (p:Person {name: $name})
            CREATE (p)-[r:ACTED_IN {roles:""" + json.dumps(row['role']) + "}]->(d)",
            id=row['id'],
            name=row['actor'],
            database_=db,
        )
print('Loaded actor nodes')

driver.close()


