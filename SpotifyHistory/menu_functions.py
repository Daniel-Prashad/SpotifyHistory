from SpotifyHistory.etl_data import extract_todays_tracks, transform_todays_tracks, load_todays_tracks, DATABASE_LOCATION
from SpotifyHistory.view_listening_history import get_most_listened
import sqlalchemy
import pandas as pd
import os

def main_menu():
    '''() -> str
    This function displays the menu options to the user, prompts for and returns the user's selection of one of these options.
    '''
    # define the list of options
    options = ['0', '1', '2', '3']

    # display the menu
    print("[1] - Add today's tracks to your all-time history")
    print("[2] - View your all time listening history")
    print("[3] - View your most listened to tracks, artists or albums")
    print("[0] - Exit program")

    # prompt for, store and return the user's selection, ensuring that the input is valid
    run = True
    while run:
        inp = input("Please select one of the options above: ")
        if inp in options:
            run = False

    if inp == '1':
        etl_todays_tracks()
    elif inp == '2':
        view_complete_history()
    elif inp == '3':
        view_most_listened()
    elif inp == '0':
        quit()

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

def view_most_listened():
    '''() -> Nonetype
    This function displays the top 1, 5 or 10 of the user's most listened to tracks, artists or albums,
    depending on the user's input.
    '''
    # define the valied options available for user input
    options = {'0': "", '1': "track_name", '2': "artist_name", '3': "album_name"}
    limit_options = {'1': 1, '2': 5, '3': 10}

    # display the user's options and ensure a valid input is provided
    print("Would you like to see your most listened to: ")
    print("[1] - Tracks")
    print("[2] - Artists")
    print("[3] - Albums")
    print("[0] - Return to main menu")
    run = True
    while run:
        inp = input("Please select one of the options above (1, 2, 3 or 0): ")
        if inp in options:
            run = False
    
    # return to the main menu if the user so chooses
    if inp == '0':
        main_menu()
    # otherwise, prompt the user for the number of records they would like to see
    else:
        print("Would you like to see the: ")
        print("[1] - Top 1")
        print("[2] - Top 5")
        print("[3] - Top 10")
        run = True
        while run:
            limit_inp = input("Please select one of the options above (1, 2, or 3): ")
            if limit_inp in limit_options:
                run = False

        # get and display the information of interest using the user's input
        most_listened_df = get_most_listened(options[inp], limit_options[limit_inp])
        print(most_listened_df)
