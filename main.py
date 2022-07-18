from SpotifyHistory.menu_functions import *


if __name__ == "__main__":
    inp = main_menu()
    if inp == '1':
        etl_todays_tracks()
    elif inp == '2':
        view_complete_history()
    elif inp == '0':
        quit()
