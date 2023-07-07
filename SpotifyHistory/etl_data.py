import pandas as pd
import sqlite3
import sqlalchemy
import datetime
import base64
import json
import webbrowser
from dateutil import parser
from requests import post, get
from urllib.parse import urlencode

DATABASE_LOCATION = "sqlite:///my_listening_history.sqlite"


def get_today_unix_timestamp():
    '''() -> int
    This function returns today's date at midnight as a unix timestamp.
    '''
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_unix_timestamp = int(today.timestamp()) * 1000
    return today_unix_timestamp


def convert_to_local_time(time_played_utc):
    '''(str) -> str, str
    This function converts the time_played attribute of each track from UTC to local time.
    '''
    utc = parser.parse(time_played_utc)
    local = utc.astimezone()
    local_date_time_played = local.strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
    local_date_played = local.strftime("%Y-%m-%d")
    local_time_played = local.strftime("%H:%M:%S:%f")[:-3]
    return(local_date_time_played, local_date_played, local_time_played)


def convert_duration(duration_ms):
    '''(int) -> str
    This function converts the duration of a song from milliseconds to minutes and seconds to be displayed to the user.
    '''
    secs = str(int(duration_ms/1000)%60)
    mins = str(int(duration_ms/(1000*60))%60)
    if len(secs) == 1:
        secs = secs + "0"
    duration_display = mins + ":" + secs
    return(duration_display)


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

def authorize_user(client_id):
    '''(str) -> str
    This function uses the Spotify Web API to generate an authorization code to validate the user.
    '''
    # define the url and HTTP headers to send to the url
    url = "https://accounts.spotify.com/authorize?"
    headers = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": "http://localhost:8888/callback",
        "scope": "user-read-recently-played"
    }
    # prompt the user to copy and paste the authorization code in the url from the window opened by the API call
    webbrowser.open(url + urlencode(headers))
    print("Please copy and paste the code provided in the url (or type 'quit' to return to the main menu):")
    auth_code = input("> ")
    return(auth_code)


def get_access_token(client_id, client_secret, auth_code):
    '''(str, str, str) -> str, Boolean
    Given the client credentials and authorization code, this function uses the Spotify Web API to generate an access token.
    '''
    # encode the client credentials to base64
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    # define the url, HTTP headers and additional data to send to the url
    url = "https://accounts.spotify.com/api/token?"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content_Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": "http://localhost:8888/callback"}
    # request and return the access token
    try:
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        access_token = json_result['access_token']
        return(access_token, False)
    # if the access token could not be retrieved then allow the user to copy and paste a new authorization code
    except:
        print("Invalid authorization code. Launching a new window to generate a new code ...")
        return("" , True)


def extract_todays_tracks(access_token):
    '''(str) -> dict
    This function uses an authorization token from Spotify in order to extract the user's listening history from the current day.
    '''
    # store today's date (at midnight) as a unix timestamp
    today_unix_timestamp = get_today_unix_timestamp()
    # define the HTTP headers to send to the url
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    # request, store and return the raw data from the Spotify API
    r = get(f"https://api.spotify.com/v1/me/player/recently-played?limit=50&after={today_unix_timestamp}", headers = headers)
    raw_data = r.json()
    return(raw_data)


def transform_todays_tracks(raw_data):
    '''(dict) -> Dataframe, Boolean
    Given the raw data, this function transforms the data, containing the user's listening history for the current day,
    into a dataframe so that today's tracks can be added to the database containing the user's complete listening history.
    '''
    # initialize the lists of attributes of interest that will be recorded from the raw data
    # and assume that the data will be transformed into the valid format 
    track_names, artist_names, album_names, track_ids, artist_ids, album_ids, release_dates, date_time_played, date_played, time_played, duration_in_ms, duration = ([] for i in range(12))
    transform_valid = True

    # loop through each track and append each attribute of the current track to the appropriate list
    try:
        for track in raw_data['items']:
            track_names.append(track['track']['name'])
            artist_names.append(track['track']['album']['artists'][0]['name'])
            album_names.append(track['track']['album']['name'])
            track_ids.append(track['track']['id'])
            artist_ids.append(track['track']['album']['artists'][0]['id'])
            album_ids.append(track['track']['album']['id'])
            release_dates.append(track['track']['album']['release_date'])
            time_played_utc = track['played_at']
            local_date_time_played, local_date_played, local_time_played = convert_to_local_time(time_played_utc)
            date_time_played.append(local_date_time_played)
            date_played.append(local_date_played)
            time_played.append(local_time_played)
            duration_ms = track['track']['duration_ms']
            duration_in_ms.append(duration_ms)
            converted_duration = convert_duration(duration_ms)
            duration.append(converted_duration)
    # otherwise, notify the user that an invalid token was provided
    except:
        print("There was a problem transforming your data.")
        transform_valid = False

    # create a dictionary using the created lists
    track_dict = {
        "track_name": track_names,
        "artist_name": artist_names,
        "album_name": album_names,
        "track_id": track_ids,
        "artist_id": artist_ids,
        "album_id": album_ids,
        "release_date": release_dates,
        "date_time_played": date_time_played,
        "date_played": date_played,
        "time_played": time_played,
        "duration_in_ms": duration_in_ms,
        "duration": duration
    }

    # store the data as a dataframe
    track_df = pd.DataFrame(track_dict, columns=['track_name', 'artist_name', 'album_name', 'track_id', 'artist_id', 'album_id',
                                                 'release_date', 'date_time_played', 'date_played', 'time_played', 'duration_in_ms', 'duration'])

    # validate and return the data
    if check_data_is_valid(track_df) and transform_valid:
        return track_df, True
    else:
        return track_df, False


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
            track_id VARCHAR(200),
            artist_id VARCHAR(200),
            album_id VARCHAR(200),
            release_date VARCHAR(200),
            date_time_played VARCHAR(200),
            date_played VARCHAR(200),
            time_played VARCHAR(200) PRIMARY KEY,
            duration_in_ms INT,
            duration VARCHAR(10)
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
            track_id VARCHAR(200),
            artist_id VARCHAR(200),
            album_id VARCHAR(200),
            release_date VARCHAR(200),
            date_time_played VARCHAR(200),
            date_played VARCHAR(200),
            time_played VARCHAR(200) PRIMARY KEY,
            duration_in_ms INT,
            duration VARCHAR(10)
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
