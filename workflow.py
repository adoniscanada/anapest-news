import logging
import logging.handlers
import datetime
from pytz import timezone
from cnn_scrape import generate_database

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
    for i in db:
        print(db[i])
    logger.info('Scraped ' + str(len(db)) + ' news articles.')