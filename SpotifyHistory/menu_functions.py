from SpotifyHistory.etl_data import extract_todays_tracks, transform_todays_tracks, load_todays_tracks, get_access_token, authorize_user
from SpotifyHistory.view_listening_history import get_days_history, get_most_listened
import re
import os
from dotenv import load_dotenv
from tabulate import tabulate


def main_menu():
    '''() -> str
    This function displays the menu options to the user, prompts for and returns the user's selection of one of these options.
    '''
    # define the list of options
    options = ['0', '1', '2', '3']

    # display the menu
    print("[1] - Add today's tracks to your all-time history")
    print("[2] - View your listening history from a certain day")
    print("[3] - View your most listened to tracks, artists or albums of all time")
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
        view_days_history()
    elif inp == '3':
        view_most_listened()
    elif inp == '0':
        quit()

def get_client_creds():
    '''() -> str, str
    This function reads and returns the client credential information from the .env file.
    '''
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    return client_id, client_secret

def etl_todays_tracks():
    '''() -> Nonetype
    This function ensures that a valid authorization code and access token are provided and calls each function involved in the ETL process.
    '''
    # store the client credential information
    client_id, client_secret = get_client_creds()
    bad_code = True
    # prompt the user to provide a valid authorization code and ensure that a valid access token is granted
    while bad_code:
        auth_code = authorize_user(client_id)
        if auth_code.lower() == 'quit':
            bad_code = False
            break
        access_token, bad_code = get_access_token(client_id, client_secret, auth_code)
    # using the valid access token, extract the data and transform it to the desired format
    if auth_code.lower() != 'quit':
        raw_data = extract_todays_tracks(access_token)
        track_df, data_valid = transform_todays_tracks(raw_data)
        # once the data is of a proper form, load the data into the database
        if data_valid:
            load_todays_tracks(track_df)
            print("Today's tracks successfully loaded!")
        else:
            print("Today's tracks were not loaded!")
            print("It looks like there were no new songs to add.")
            print("Try listening to a few songs, then try again.")
            print("Returning to main menu.")
    main_menu()


def view_days_history():
    '''() -> Nonetype
    This function displays the user's complete listening history of a given day.
    '''
    # ensure that the date provided is valid
    run = True
    while run:
        inp_date = input("Please enter day for which you would like to see your listening history in YYYY-mm-dd format (or type 'quit' to return to the main menu): ")
        if inp_date.lower() == 'quit':
            main_menu()
            run = False
        elif re.match('^[0-9]{4}-[0-1]{1}[0-9]{1}-[0-3]{1}[0-9]{1}$', inp_date):
            run = False
        else:
            print("Invalid date provided.")
    # output the user's listening history for the provided date
    if inp_date != 'quit':
        df = get_days_history(inp_date)
        if df.empty:
            print("There are no recorded songs for this date.")
        else:
            print(tabulate(df, headers="keys", tablefmt="fancy_outline"))


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
        print(tabulate(most_listened_df, headers="keys" ,tablefmt="fancy_outline"))

