import requests
from bs4 import BeautifulSoup
import datetime

NEWS_URL = 'https://www.cnn.com'
START_STR = '(CNN)'

def scrape_for_links(keyword : str) -> set:
    links = set()
    
    try:
        response = requests.get(NEWS_URL)
        response.raise_for_status()
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        for link in soup.find_all('a'):
            ref = link.get('href')
            if type(ref) == str and keyword in ref:
                links.add(NEWS_URL + ref)
    except:
        pass
    
    return links

def scrape_article(link : str) -> tuple:
    title = ''
    text = ''
    
    try:
        response = requests.get(link)
        response.raise_for_status()
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string
        p = soup.find_all('p')

        start = 0
        for i in p:
            if START_STR in i:
                start = i + 1
                break
        
        paragraphs = [i.text.strip() for i in p[start:] if i.text[0] == '\n' and '.' in i.text]
        text = ' '.join(paragraphs)
    except:
        pass

    if len(text) > 0:
        return (title, text)
    
    return (None, None)

def generate_database(day : datetime.date):
    keyword = day.strftime('%Y/%m/%d')
    database = {}
    links = scrape_for_links(keyword)
    for link in links:
        article = scrape_article(link)
        if article[0] != None:
            database[article[0]] = article[1]
    return database