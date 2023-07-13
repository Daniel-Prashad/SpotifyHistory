from SpotifyHistory.etl_data import DATABASE_LOCATION
import sqlalchemy
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D


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


def get_num_songs_by_time(time):
    '''(str) -> int
    Given the hour, this function returns the total number of songs that have been listened to at that hour throughout the user's listening history.
    '''
    query = """
        SELECT COUNT(*) AS num_songs
        FROM complete_listening_history
        WHERE time_played LIKE "{time}:__:__:___"
        """.format(time=time)
    # establish a connection to the database
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    # store and return the sum of listening duration for the given date
    num_songs = pd.read_sql_query(sql=query, con=engine)
    return(num_songs["num_songs"][0])


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


def add_value_labels(durations_in_ms, duration_labels, plot, double = False):
    '''(list of int, list of str, matplotlib.axes._axes.Axes, Boolean) -> Nonetype
    This function adds value labels on the bar graph where duration_labels is the text to be added at the corresponding y-coordinate durations_in_ms.
    '''
    for i in range(len(duration_labels)):
        if double == False:
            plot.text(i - 0.35/2, durations_in_ms[i], duration_labels[i])
        else:
            plot.text(i + 0.35/2, durations_in_ms[i], duration_labels[i])


def add_value_labels_scatter(durations_in_ms, duration_labels, plot):
    '''(list of int, list of str, matplotlib.axes._axes.Axes) -> Nonetype
    This function adds value labels on the scatter plot where duration_labels is the text to be added at the corresponding y-coordinate durations_in_ms.
    '''
    for i in range(len(duration_labels)):
        if durations_in_ms[i] > 0:
            plot.text(i, durations_in_ms[i] + 200000, duration_labels[i], color="green")
        elif durations_in_ms[i] < 0:
            plot.text(i, durations_in_ms[i] - 200000*3, duration_labels[i], color="red")
        else:
            plot.text(i, durations_in_ms[i] + 200000, duration_labels[i], color="black")


def plot_num_songs_by_time(time_labels, num_songs):
    '''(list of str, list of int) -> Nonetype
    This function outputs a bar chart showing the total number of songs played by time of day.
    '''
    # make a bar chart where the x-coordinates are the times of the day and the height of each bar is the corresponding number of songs played
    plt.bar(time_labels, num_songs)
    # set the title and axis labels
    plt.title("Total Number of Songs Listened by Time of Day")
    plt.ylabel("Total Number of Songs")
    plt.xlabel("Time of Day")
    # rotate the x ticks to be vertical
    plt.xticks(rotation=90)
    # label each of the bars with the corresponding number of songs
    for i in range(len(num_songs)):
        if num_songs[i] != 0:
            plt.text(i, num_songs[i], num_songs[i])
    # show the plot
    plt.show()


def plot_daily_duration(week_dates, durations_in_ms, duration_labels):
    '''(list of str, list of int, list of str) -> Nonetype
    This function outputs a bar chart showing the user's daily time spent listening to music for the given week.
    '''
    # store the days of the week in a list to be used as the x-axis labels
    days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    # make a bar chart where the x-coordinates are the days of the week and the height of each bar is the corresponding time spent listening to music
    plt.bar(days_of_week, durations_in_ms)
    # set the title and y-axis label
    plt.title("Time Spent Listening By Day For " + week_dates[0] + " to " + week_dates[6])
    plt.ylabel("Time Spent Listening")
    # remove the y-axis ticks
    ax = plt.gca()
    ax.set_yticks([])
    # add the value labels for each bar
    add_value_labels(durations_in_ms, duration_labels, ax)
    # show the bar chart
    plt.show()
    

def plot_weekly_comparison(all_dates, all_durations_in_ms, all_duration_labels, duration_differences, duration_difference_labels):
    '''(list of str, list of int, list of str, list of int, list of str) -> Nonetype
    This function outputs a double bar chart showing the user's daily time spent listening to music for the past two weeks
    and a scatterplot comparing the time spent listening per day between the two weeks.
    '''
    # store the days of the week in a list to be used as the x-axis labels
    days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    # set the locations for the bars along the x-axis and the width of the bars
    x = np.arange(len(days_of_week))
    width = 0.35
    # create a set of two subplots
    fig, ax = plt.subplots(2,1)

    # DOUBLE BAR CHART
    # plot the bars in the first subplot
    two_weeks_ago = ax[0].bar(x, all_durations_in_ms[0], width=width)
    one_week_ago = ax[0].bar(x + width, all_durations_in_ms[1], width=width)
    # set the title, axis labels and legend of the first subplot
    ax[0].set_title("Comparing Time Spent Listening By Day For The Last Two Weeks")
    ax[0].set_ylabel("Time Spent Listening")
    ax[0].set_yticks([])
    ax[0].set_xticks(x + width/2)
    ax[0].set_xticklabels(days_of_week)
    ax[0].legend((two_weeks_ago, one_week_ago), (all_dates[0][0] + " to " + all_dates[0][6], all_dates[1][0] + " to " + all_dates[1][6]))
    # add the value labels for each bar
    for i in range(len(all_duration_labels)):
        if (i + 1) % 2 == 1:
            add_value_labels(all_durations_in_ms[i], all_duration_labels[i], ax[0], False)
        else:
            add_value_labels(all_durations_in_ms[i], all_duration_labels[i], ax[0], True)
    
    # SCATTER PLOT
    # define the colour to be used for each point and plot each point of the scatterplot on the second subplot
    for i in range(len(duration_differences)):
        if duration_differences[i] > 0:
            colour = "green"
        elif duration_differences[i] < 0:
            colour = "red"
        else:
            colour = "black"
        ax[1].scatter(days_of_week[i], duration_differences[i], color=colour)
    # connect the points with a line
    ax[1].plot(days_of_week, duration_differences, color="grey")
    # add value labels for each point
    add_value_labels_scatter(duration_differences, duration_difference_labels, ax[1])
    # add a horizontal line at y=0
    ax[1].axhline(0, color="grey", linestyle="--")
    # set the title and axis labels for the second subplot
    ax[1].set_title("Difference In Time Spent Listening By Day For " + all_dates[1][0] + " - " + all_dates[1][6] + " Compared To " + all_dates[0][0] + " - " + all_dates[0][6])
    ax[1].set_ylabel("Difference In Time Spent Listening")
    ax[1].set_yticks([])
    # set the legend of the second subplot
    legend_elements = [Line2D([0],[0], marker='o', color='white', markerfacecolor='green', label="Listened More Last Week"),
                       Line2D([0],[0], marker='o', color='white', markerfacecolor='red', label="Listened Less Last Week")]
    ax[1].legend(handles=legend_elements)

    # show the two subplots
    plt.show()