import json
import datetime
from pytz import timezone
from cnn_scrape import generate_database

if __name__ == '__main__':
    tz = timezone('US/Eastern')
    now = datetime.datetime.now(tz)
    db = generate_database(now.date())
    for i in db:
        print(db[i])