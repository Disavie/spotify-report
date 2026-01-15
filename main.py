import spotify
import myemail
import visualizer
import threading

stop_event = threading.Thread()
"""
    commands are:
    start
    stop
    quit
    sort -> prompt how to be sorted >>
    push -> sends notification now  >>
    save -> saves now           
    search -> prints info about certain song (regex to find similar title songs?)

"""
MY_EMAIL = "davisstermer@gmail.com"

def main():
    is_running = 0
    while True:
        cmd = input("> ").strip().lower()

        if cmd == "start":
            is_running = 1
            spotify.start()

        elif cmd == "stop":
            is_runing = 0
            spotify.stop()

        elif cmd == "quit":
            spotify.stop()
            is_running = 0
            break
        elif cmd == "sort":
            try:
                val = input("enter condition to sort by (times_played, seconds_listened, etc)\n> ").strip().lower()
                visualizer.parse_that_shit(val)
                print("dumped sorted in sorted.json (descending)")
            except KeyError:
                print("KeyError, did you have a typo?")
        elif cmd == "push":
            myemail.send_email(myemail.MY_EMAIL,"Requested Daily Notification", spotify.get_todays_stats())
        elif cmd == "save":
            if is_running:
                spotify.safe_save()
            else:
                print("saving before program running is not allowed")
        
if __name__ == "__main__":
    main()