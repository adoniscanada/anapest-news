# anapest-news
A program that scrapes CNN articles and formats them into anapest poems.

## Usage
```python main.py -b <banned-words> -m <meter> -l <line-length>```

Banned Words: an array of words (lowercase and separated by commas) that will not be considered in poem generation (e.g: cnn,newspaper,...)

Meter: an array of 1 and 0 representing stresses and non-stresses (e.g: 0,0,1)

Line Length: desired line length.

## Acknowledgments
The CMU Pronouncing Dictionary: http://www.speech.cs.cmu.edu/cgi-bin/cmudict

CNN: https://www.cnn.com/
