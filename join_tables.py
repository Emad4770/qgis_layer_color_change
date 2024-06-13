import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime
from psycopg2.extras import execute_values


# Function to get user input date
def get_user_date():
    while True:
        user_date = input("Please enter the date in YYYY-MM-DD format: ")
        try:
            return datetime.strptime(user_date, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Please try again.")


# Function to load data from the PostgreSQL database
def load_data(db_params):
    conn_string = (f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:"
                   f"{db_params['port']}/{db_params['dbname']}")
    engine = create_engine(conn_string)

    # Load the GeoPackage layer
    # gdf1 = gpd.read_postgis('SELECT p_id, leakage_prob, geom FROM gis_data.pipes', engine, geom_col='geom')
    gdf1 = pd.read_sql('SELECT p_id, probability FROM gis_data_test.pipes', engine)

    # Load the leakage probability table
    df2 = pd.read_sql('SELECT * FROM gis_data.leakage_prob', engine)

    df2['timestamp'] = pd.to_datetime(df2['timestamp'])

    return gdf1, df2


# Function to filter and get the latest records up to the specified date
def filter_latest_records(df2, user_date):
    df2_filtered = df2[df2['timestamp'] <= user_date]
    df2_filtered = df2_filtered.sort_values(by=['p_id', 'timestamp'])
    latest_records = df2_filtered.groupby('p_id').last().reset_index()
    return latest_records


# Function to update leakage probability in the first table
def update_leakage_probability(gdf1, latest_records):
    merged_df = gdf1.merge(latest_records[['p_id', 'probability']], on='p_id', suffixes=('', '_latest'), how='left')
    gdf1['probability'] = merged_df['probability_latest'].combine_first(gdf1['probability'])
    return gdf1


# Function to execute the update queries on the PostgreSQL database
def execute_update(gdf1, db_params):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    update_query = """
        UPDATE gis_data_test.pipes
        SET probability = data.probability
        FROM (VALUES %s) AS data (id, probability)
        WHERE pipes.p_id = data.id;
    """

    update_data = list(zip(gdf1['p_id'], gdf1['probability']))
    execute_values(cursor, update_query, update_data)

    conn.commit()
    cursor.close()
    conn.close()


# Main function to coordinate the steps
def main():
    db_params = {
        # 'schema': 'gis_data',
        'dbname': 'qwc_services',
        'user': 'postgres',
        'password': 'admin',
        'host': 'localhost',
        'port': '5432'
    }

    # user_date = get_user_date()
    user_date = "2018-01-01"
    gdf1, df2 = load_data(db_params)
    latest_records = filter_latest_records(df2, user_date)
    updated_gdf1 = update_leakage_probability(gdf1, latest_records)
    execute_update(updated_gdf1, db_params)

    print("GeoPackage layer updated successfully.")


# Run the main function
if __name__ == "__main__":
    main()
