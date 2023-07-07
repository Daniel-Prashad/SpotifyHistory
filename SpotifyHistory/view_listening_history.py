from SpotifyHistory.etl_data import DATABASE_LOCATION
import sqlalchemy
import pandas as pd


def get_days_history(inp_date):
    '''(str) -> Dataframe
    Given a date, this function returns a dataframe containing the complete listening
    history for the provided date.
    '''
    # define the query depending on the desired date
    query = """
        SELECT track_name, artist_name, album_name, release_date, date_played, time_played, duration
        FROM complete_listening_history WHERE date_played = "{inp_date}" ORDER BY time_played
    """.format(inp_date=inp_date)
    # establish a connection to the database
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    # retrieve, increment the index and return the dataframe based on the above query
    df = pd.read_sql_query(sql=query, con=engine)
    df.index += 1
    return(df)


def get_most_listened(column, limit):
    '''(str, int) -> Dataframe
    Given a column in the dataframe and a limit, this function returns a dataframe containing the
    top 1, 5 or 10 tracks, artists or albums listened to by the user. 
    '''
    # define the query depending on the desired column and limit
    query = """
        SELECT {column}, COUNT(*) AS num_of_listens FROM complete_listening_history
        GROUP BY {column}
        ORDER BY COUNT(*) DESC, {column}
        LIMIT {limit}
        """.format(column=column, limit=limit)
    # establish a connection to the database
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    # retrieve, increment the index and return the dataframe based on the above query
    most_listened_df = pd.read_sql_query(sql=query, con=engine)
    most_listened_df.index += 1
    return(most_listened_df)

