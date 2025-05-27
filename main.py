import logging
import logging.handlers
import pickle
import json
import datetime
from pytz import timezone
from cnn_scrape import generate_database
from gen_poem import generate_poem

# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "workflow.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter('%(asctime)s %(message)s')
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

if __name__ == '__main__':
    tz = timezone('US/Eastern')
    now = datetime.datetime.now(tz)
    db = generate_database(now.date())
    
    logger.info('Scraped ' + str(len(db)) + ' news articles.')
    
    poems = []
    for i in db.values():
        poems.append(generate_poem(i.split()))
    
    with open('current_poems.json', 'w') as file:
        json.dump(poems, file)
    
    logger.info('Generated poems.')