# Spotify Listening History Management
This program creates and manages a database contining the user's Spotify listening history. It allows the user to add the current day's listening history and view various statistics about their listening habits, such as their favourite tracks, artists and albums.

# Instructions
1. Download all files and ensure that the file structure is maintained.
2. Open a new terminal and change your current working directory to the SpotifyHistory folder downloaded in step 1.
3. It is recommended to create and activate a virtual environment before continuing.
3. Ensure that the below python libraries are installed by running the following:
   * pip install pandas
   * pip install sqlalchemy
   * pip install tabulate
4. To start the program, run the following command:
   * python main.py
5. To add the current day's listening history:
   a. Select the first option from the menu
   b. Open the following link in your web browser: https://developer.spotify.com/console/get-recently-played/
      * Note that in order to continue you will need to be logged into your Spotify account and allow access to pull your recently played tracks
   c. Click "Get Token"
   d. Click the checkbox next to "user-read_recently_played"
   e. Click "Request Token"
   f. Copy the full token under "OAuth Token"
   g. Returning to the program, right click in the terminal to paste the copied token in the previous step and press the Enter key to finish
