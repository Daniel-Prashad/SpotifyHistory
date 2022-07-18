import requests
import pandas as pd
import sqlite3
import sqlalchemy
import datetime

DATABASE_LOCATION = "sqlite:///my_listening_history.sqlite"


def get_today_unix_timestamp():
    '''() -> int
    This function returns today's date at midnight as a unix timestamp.
    '''
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_unix_timestamp = int(today.timestamp()) * 1000
    return today_unix_timestamp


def check_data_is_valid(df):
    '''(Dateframe) -> Boolean
    This function determines whether the data extracted and transformed is in the condition to be loaded into the database.
    '''
    # check for empty dataframe
    if df.empty:
        print("No songs found. Try listening to a few songs, then generate a new token.")
        return False

    # check for duplicates
    if not pd.Series(df['time_played']).is_unique:
        raise Exception("Duplicate records found. Try listening to a few songs, then generate a new token.")

    return True


def extract_todays_tracks(token):
    '''(str) -> dict
    This function uses an authorization token from Spotify in order to extract the user's listening history from the current day.
    '''
    # store today's date (at midnight) as a unix timestamp
    today_unix_timestamp = get_today_unix_timestamp()
    # define the HTTP headers to send to the url
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    # request, store and return the raw data from the Spotify API
    r = requests.get(f"https://api.spotify.com/v1/me/player/recently-played?limit=50&after={today_unix_timestamp}", headers = headers)
    raw_data = r.json()      
    return(raw_data)


def transform_todays_tracks(raw_data):
    '''(dict) -> Dataframe, Boolean
    Given the raw data, this function transforms the data, containing the user's listening history for the current day,
    into a dataframe so that today's tracks can be added to the database containing the user's complete listening history.
    '''
    # initialize the lists of attributes of interest that will be recorded from the raw data
    # and assume that the token provided was valid 
    track_names = []
    artist_names = []
    album_names = []
    release_dates = []
    date_played = []
    time_played = []
    bad_token = False

    # loop through each track and append each attribute of the current track to the appropriate list
    try:
        for track in raw_data['items']:
            track_names.append(track['track']['name'])
            artist_names.append(track['track']['album']['artists'][0]['name'])
            album_names.append(track['track']['album']['name'])
            release_dates.append(track['track']['album']['release_date'])
            date_played.append(track['played_at'][0:10])
            time_played.append(track['played_at'])
    # otherwise, notify the user that an invalid token was provided
    except:
        print("Invalid token. Please generate a new token and try again.")
        bad_token = True

    # create a dictionary using the created lists
    track_dict = {
        "track_name": track_names,
        "artist_name": artist_names,
        "album_name": album_names,
        "release_date": release_dates,
        "date_played": date_played,
        "time_played": time_played
    }

    # store the data as a dataframe
    track_df = pd.DataFrame(track_dict, columns=['track_name', 'artist_name', 'album_name', 'release_date', 'date_played', 'time_played'])

    # validate and return the data
    if bad_token:
        return track_df, bad_token
    if check_data_is_valid(track_df):
        return track_df, bad_token


def load_todays_tracks(track_df):  
    '''(Dataframe) -> Nonetype
    This function establishes a connection with the database, creates a new table to store today's listening history and
    appends the tracks listened to today to the complete listening history.
    '''
    # establish the sqlalchemy engine, the connection to the database and the cursor to execute SQL commands
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    conn = sqlite3.connect('my_listening_history.sqlite')
    cursor = conn.cursor()

    # create a table to store the user's complete listening history if one does not already exist
    create_query = """
        CREATE TABLE IF NOT EXISTS complete_listening_history(
            track_name VARCHAR(200),
            artist_name VARCHAR(200),
            album_name VARCHAR(200),
            release_date VARCHAR(200),
            date_played VARCHAR(200),
            time_played VARCHAR(200) PRIMARY KEY
        );
        """
    cursor.execute(create_query)

        
    # drop the table containing yesterday's listening history
    drop_yesterday_query = """
        DROP TABLE IF EXISTS todays_tracks;
    """
    cursor.execute(drop_yesterday_query)

    # create a table to store today's listening history and load today's tracks
    create_today_query = """
        CREATE TABLE IF NOT EXISTS todays_tracks(
            track_name VARCHAR(200),
            artist_name VARCHAR(200),
            album_name VARCHAR(200),
            release_date VARCHAR(200),
            date_played VARCHAR(200),
            time_played VARCHAR(200) PRIMARY KEY
        );
    """
    cursor.execute(create_today_query)
    try:
        track_df.to_sql(name='todays_tracks', con=engine, if_exists='append', index=False)
    except:
        print("Data not loaded :(")

    # add today's tracks to the complete listening history
    add_todays_tracks_query = """
        INSERT OR IGNORE INTO complete_listening_history
        SELECT * FROM todays_tracks;
    """
    cursor.execute(add_todays_tracks_query)

    # commit the changes and close the connection to the database
    conn.commit()
    conn.close()
