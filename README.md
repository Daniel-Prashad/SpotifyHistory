# Spotify Listening History Management
This program creates and manages a database containing the user's Spotify listening history. It allows the user to add the current day's listening history and view various statistics about their listening habits, such as their favourite tracks, artists and albums. Furthermore, it displays graphs detailing the user's listening habits. This includes the user's favourite times of the day to listen to music, their total time spent listening by day for the current week and a graph comparing their last two weeks of listening history, which includes a t-test verifying whether a difference between the two weeks is significant.

# Instructions
1. Download all files and ensure that the file structure is maintained.
2. Open a new terminal and change your current working directory to the folder downloaded in step 1.
3. It is recommended to create and activate a virtual environment before continuing.
3. Ensure that the below python libraries are installed by running the following:
   * pip install matplotlib
   * pip install pandas
   * pip install sqlalchemy
   * pip install tabulate
4. Complete the following steps to setup a connection for the api calls (this only needs to be done once):
      * Login to your Spotify account and open the following link in your web browser: https://developer.spotify.com/dashboard
      * Click "Create app"
      * Enter a name and description for the app in the approriate sections ("Website" can be left blank)
      * Copy and paste "http://localhost:8888/callback" into the "Redirect URI" section
      * Agree to the TOS and click "Save"
      * Open your newly created app from your dashboard
      * Click "Settings" in the top-right corner of the screen
      * Copy your "Client ID" and paste it into the "CLIENT_ID" string in the local .env file
      * Click "View client secret" and copy and paste it into the "CLIENT_SECRET" string in the local .env file
      * Save the changes made to the local .env file
4. To start the program, run the following command:
   * python main.py
5. To add the current day's listening history:
   * Select the first option from the menu
   * This will open a webpage with the URL: "http://localhost:8888/callback?code=[generated code]"
   * Copy and paste the entire generated code into the terminal and press [Enter]
