from SpotifyHistory.etl_data import extract_todays_tracks, transform_todays_tracks, load_todays_tracks, DATABASE_LOCATION
import sqlalchemy
import pandas as pd

def main_menu():
    '''() -> str
    This function displays the menu options to the user, prompts for and returns the user's selection of one of these options.
    '''
    # define the list of options
    options = ['0', '1', '2']

    # display the menu
    print("[1] - Add today's tracks to your all-time history")
    print("[2] - View your all time listening history")
    print("[0] - Exit program")

    # prompt for, store and return the user's selection, ensuring that the input is valid
    run = True
    while run:
        inp = input("Please select one of the options above: ")
        if inp in options:
            run = False
    return inp


def etl_todays_tracks():
    '''() -> Nonetype
    This function ensures that a valid token is provided and calls each function involved in the ETL process.
    '''
    bad_token = True
    # prompt the user to provide a valid token and extract and transform the data
    while bad_token:
        print("Please copy and paste the Spotify Token here (or type 'quit' to return to the main menu):")
        inp_token = input("> ")
        if inp_token.lower() == 'quit':
            main_menu()
            break
        raw_data = extract_todays_tracks(inp_token)
        track_df, bad_token = transform_todays_tracks(raw_data)
    # once the data is of a proper form, load the data into the database
    load_todays_tracks(track_df)


def view_complete_history():
    '''() -> Nonetype
    This function displays the user's complete listening history.
    '''
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    select_query = pd.read_sql_query(sql="SELECT * FROM complete_listening_history ORDER BY time_played DESC;", con=engine)
    df = pd.DataFrame(select_query, columns=['track_name', 'artist_name', 'album_name', 'release_date', 'date_played', 'time_played'])
    print(df)