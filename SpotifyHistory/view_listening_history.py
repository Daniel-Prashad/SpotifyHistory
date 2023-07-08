from SpotifyHistory.etl_data import DATABASE_LOCATION
import sqlalchemy
import pandas as pd
from matplotlib import pyplot as plt


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


def get_total_duration(date):
    '''(str) -> int
    Given a date, this function returns the total duration spent listening to music on that date in milliseconds.
    '''
    query = """
        SELECT COALESCE(SUM(duration_in_ms), 0) AS total_duration
        FROM complete_listening_history
        WHERE date_played = "{date}"
        """.format(date=date)
    # establish a connection to the database
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    # store and return the sum of listening duration for the given date
    duration_in_ms = pd.read_sql_query(sql=query, con=engine)
    return(duration_in_ms["total_duration"][0])


def add_value_labels(durations_in_ms, duration_labels):
    '''(list of int, list of str) -> Nonetype
    This function adds value labels on the plot where duration_labels is the text to be added at the corresponding y-coordinate durations_in_ms.
    '''
    for i in range(len(duration_labels)):
        plt.text(i, durations_in_ms[i], duration_labels[i])


def plot_daily_duration(week_dates, durations_in_ms, duration_labels):
    '''(list of str, list of int, list of str) -> Nonetype
    This function outputs a bar chart showing the user's daily time spent listening to music for the given week.
    '''
    # store the days of the week in a list to be used as the x-axis labels
    days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    # make a bar chart where the x-coordinates are the days of the week and the height each bar is the corresponding time spent listening to music
    plt.bar(days_of_week, durations_in_ms)
    # set the title and y-axis label
    plt.title("Time Spent Listening By Day For " + week_dates[0] + " to " + week_dates[6])
    plt.ylabel("Time Spent Listening")
    # remove the y-axis ticks
    ax = plt.gca()
    ax.set_yticks([])
    # add the value labels for each bar
    add_value_labels(durations_in_ms, duration_labels)
    # show the bar chart
    plt.show()
    