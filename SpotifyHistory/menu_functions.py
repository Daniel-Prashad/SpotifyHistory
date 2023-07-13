from SpotifyHistory.etl_data import extract_todays_tracks, transform_todays_tracks, load_todays_tracks, get_access_token, authorize_user, convert_duration
from SpotifyHistory.view_listening_history import get_days_history, get_most_listened, get_total_duration, plot_daily_duration, plot_weekly_comparison
import re
import os
from dotenv import load_dotenv
from tabulate import tabulate
import datetime


def main_menu():
    '''() -> str
    This function displays the menu options to the user, prompts for and returns the user's selection of one of these options.
    '''
    # define the list of options
    options = ['0', '1', '2', '3', '4', '5']

    # display the menu
    print("[1] - Add today's tracks to your all-time history")
    print("[2] - View your listening history from a certain day")
    print("[3] - View your most listened to tracks, artists or albums of all time")
    print("[4] - View your listening time for the current week")
    print("[5] - Compare your last two full weeks of listening history")
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
    elif inp == '4':
        view_daily_duration_listened()
    elif inp == '5':
        compare_previous_two_weeks()
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


def get_week_dates(date):
    '''(datetime.date) -> list of str
    This function returns the dates of the week for the given date.
    '''
    # store the current date's number of the week (ex. Sunday = 0, Monday = 1, ... Saturday = 6)
    day_i = (date.weekday() + 1) % 7
    # store and set the date of the first day of the week, Sunday
    sunday = date - datetime.timedelta(days = day_i)
    date = sunday
    # return each date of the current week from Sunday to Saturday
    for i in range(7):
        yield date.isoformat() 
        date += datetime.timedelta(days=1)


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


def view_daily_duration_listened():
    '''() -> Nonetype
    This function gets the data required and calls a function to output a bar chart showing the user's daily time spent listening to music for the current week.
    '''
    # store today's date
    today = datetime.datetime.now().date()
    # get and store the dates for the current week
    week_dates = [d for d in get_week_dates(today)]
    durations_in_ms = []
    duration_labels = []
    # for each day of the week, get the total time spent listening in milliseconds and convert to H:M:S
    for date in week_dates:
        duration_in_ms = get_total_duration(date)
        durations_in_ms.append(duration_in_ms)
        duration_labels.append(convert_duration(duration_in_ms))
    # output the bar graph
    plot_daily_duration(week_dates, durations_in_ms, duration_labels)


def compare_previous_two_weeks():
    '''() -> Nonetype
    This function gets the data required and calls a function to output a double bar chart showing the user's daily time spent listening to music for the past two weeks
    and a scatterplot comparing the time spent listening per day between the two weeks.
    '''
    # store today's date and set the offsets to calculate the dates for the past two weeks
    today = datetime.datetime.now().date()
    offset = [14, 7]
    # initialize the lists to store all the dates, durations spent listening and duration labels
    all_dates = []
    all_durations_in_ms = []
    all_duration_labels = []
    # get the date for each day in the past two full weeks
    for i in range(len(offset)):
        durations_in_ms = []
        duration_labels = []
        date = today - datetime.timedelta(days=offset[i])
        week_dates = [d for d in get_week_dates(date)]
        # get the duration listened and duration labels for each date
        for d in week_dates:
            duration_in_ms = get_total_duration(d)
            durations_in_ms.append(duration_in_ms)
            duration_labels.append(convert_duration(duration_in_ms))
        # add all the data to the corresponding main list
        all_dates.append(week_dates)
        all_durations_in_ms.append(durations_in_ms)
        all_duration_labels.append(duration_labels)

    #################################################################################### TESTING ####################################################################################
    #all_durations_in_ms = [[3600000, 4000000, 7200000, 8000000, 5400000, 3050000, 9250000], [7074553, 3959502, 4138418, 8523539, 9468900, 7746597, 3277002]]
    #all_duration_labels = [["1:00:00", "1:06:40", "2:00:00", "2:13:20", "1:30:00", "50:50", "2:34:10"], ["1:57:54", "1:05:59", "1:08:58", "2:22:03", "2:37:48", "2:09:06", "54:37"]]
    #################################################################################### TESTING ####################################################################################
    
    # split the durations of each week into separate lists
    durations_one_wk_ago = all_durations_in_ms[1]
    durations_two_wks_ago = all_durations_in_ms[0]
    # calculate and store the difference in time spent listening between one week ago and two weeks ago for each day of the week
    duration_differences = [durations_one_wk_ago_i - durations_two_wks_ago_i for durations_one_wk_ago_i, durations_two_wks_ago_i in zip(durations_one_wk_ago, durations_two_wks_ago)]
    # convert each difference from milliseconds to H:M:S
    duration_difference_labels = []
    for d in duration_differences:
        duration_difference_labels.append(convert_duration(abs(d)))
    # calculate and output the total weekly difference in time spent listening
    weekly_difference_ms = sum(duration_differences)
    weekly_difference = convert_duration(abs(weekly_difference_ms))
    more_or_less = " more" if weekly_difference_ms >= 0 else " less"
    print("You spent a total of " + weekly_difference + more_or_less + " listening from " + all_dates[1][0] + " to " + all_dates[1][6] + " than from " + all_dates[0][0] + " to " + all_dates[0][6] + ".")
    # output the two graphs
    plot_weekly_comparison(all_dates, all_durations_in_ms, all_duration_labels, duration_differences, duration_difference_labels)