from apartmentBot import scrape_for_apartments
import time
import settings
import traceback
import sys

while True:
    print("{}: Starting interval run.".format(time.ctime()))
    sys.stdout.flush()
    try:
        scrape_for_apartments()
    except KeyboardInterrupt:
        print("Exiting....")
        sys.stdout.flush()
        sys.exit(1)
    except Exception as exc:
        print("Error with the scraping:", sys.exc_info()[0])
        sys.stdout.flush()
        traceback.print_exc()
        print(f"Sleeping for {settings.SLEEP_TIMER/60} minutes.")
        sys.stdout.flush()
        time.sleep(settings.SLEEP_TIMER)
    else:
        print("{}: Done running. Sleeping.".format(time.ctime()))
        sys.stdout.flush()
        time.sleep(settings.SLEEP_TIMER)
