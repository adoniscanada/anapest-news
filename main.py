import argparse
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

# Main
if __name__ == '__main__':
    tz = timezone('US/Eastern')
    now = datetime.datetime.now(tz)
    db = generate_database(now.date())

    desc = 'Poem generator from CNN articles'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-m', '--Meter', help='Set meter', default='0,0,1')
    parser.add_argument('-b', '--Banned', help='Set list of words not to be considered in poem generation', default='')
    parser.add_argument('-ll', '--Line', help='Set line length', default=3)
    parser.add_argument('-pl', '--Poem', help='Set poem length', default=480)
    parser.add_argument('-o', '--Output', help='Set output file', default='poems.json')
    args = parser.parse_args()

    poems = {}
    for i in db.keys():
        p = generate_poem(db[i].split(), [b for b in args.Banned.split(',')], [int(m) for m in args.Meter.split(',')], int(args.Line), int(args.Poem))
        poems[i] = p

    with open(args.Output, 'w') as file:
        json.dump(poems, file)
    
    logger.info('Generated ' + str(len(poems)) + ' poems with the arguments:' + str(args))