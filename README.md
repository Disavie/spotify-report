spotify-report

A daily, weekly, and yearly Spotify “mini-wrapped” that summarizes your listening habits and trends.

Test


commit #14 : 
    1/17/26
    added genre tracking
    added some comments in spotify.spotify_loop
    backfill genretracking, artistid, track lengths
    

-> set recipient email command
-> genre tracker
-> notification data parsing:
    top 5 songs
    top 5 artists
    top genre

commit #13:
    stopify loop is on a thread now
    command line access;
        start
        stop
        quit
        sort
        save
        push -> sends notification


commit #12: hourly notifications

commit #11 : 1/15/26
    visualizer.py to do some basic parsing of data.json
    tracks length of tracks now

commit #10: 1/15/26
    fixed midnight crash errror with START_TIME -> current_day

commit #9 1/14/26:
    added email error notifcations,
->add daily email summary
        -> top song
        -> top artist
        -> top genre
        -> listening time
->genre tracking



commit 8.5 1/13/26:
    daily second tracker big ass bug fixed yay!


*next commit add genre and email notifications
commit 8: 1/13/26
    fixed/handled network timeout (try except continue)
    autosave now occurs after 15 minutes
    autosave says the actual time instead of timestamp

commit 7: 1/12/26
    fixed pause issue almost certainly
    fixed issue with timeout when internet cuts out i think?
    counts skips
    genre support in future
-> do daily mini-wrapped's tomorrow
-> need command line access to request specific info, put main loop into a new thread   
-> send me an email if program crashes too alongside a crash report 

commit 6: 1/12/26
    fixed pause issue i think -> next time count skips

commit 5: 1/12/26
    PROBLEM: FIX ISSUE WITH PAUSE!!!

c4.5:
zach idea -> how often do songs get skipped when shuffle is enabled
? good way to implement?

commit 4: 1/12/26
anima idea -> skip rates:
count how often x song skipped
count how often songs of x genre get skipped
    METHOD: use item/duration_ms in song["item] compare to +/- 5s of when update_data() changes amount of time spent listening to that song
-> track genres of tracks
-> track skips of songs
---> wont directly allow for seeing how often x genre gets skipped but can aggregate these two statistics to see


commit 3: 1/12/26
    stores per-track information across sessions
    stores per-day information (total listening minutes)

-> automatically email report of total minutes listened in the past day and top song
-> how can i track top song of the day>
    ->list of songs listened to today
    ->amount of time spent listening to each today
ex.
{
    today:{ //today's stats, resets

    },
    tracks:{ //all time stats about all songs listened to

    },
    dates:{ //history of all past days

    }
}

---------------------
for email try this:
import smtplib
from email.message import EmailMessage
import ssl # For a secure connection

# --- Email Credentials and Content ---
sender_email = "your_email@gmail.com"
app_password = "your_generated_app_password" # Use the app password, not your normal password
receiver_email = "recipient_email@example.com"
subject = "Automated Email from Python"
body = "This is a simple automated email sent using Python."

# Create the email message object
msg = EmailMessage()
msg.set_content(body)
msg['Subject'] = subject
msg['From'] = sender_email
msg['To'] = receiver_email

# --- Send the Email via Gmail's SMTP Server ---
smtp_server = "smtp.gmail.com"
smtp_port = 587 # Port for TLS encryption

try:
    # Create a secure SSL context
    context = ssl.create_default_context()

    # Connect to the server and start TLS encryption
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()  # Optional, but good practice
        server.starttls(context=context)
        server.login(sender_email, app_password)
        server.send_message(msg)
        print("Email sent successfully!")

except smtplib.SMTPException as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")



commit 2: 1/12/26
    stores some limited data across sessions
    bugs?
-> automatically email a report of:
     most listened to songs in past 24hrs
     total minutes listened in past 24hrs
     top artist over the past 24hrs

     
commit 1: 1/12/26
    have janky oauth token
    minutes listened since program started
    current song
    
-> can i get updates of when song changes instead of polling constantly?
^ i dont think i can do this, i need to constantly poll as far as i can tell