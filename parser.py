from random import randint
import psycopg2
import time 
import os
import sys
import requests
from bs4 import BeautifulSoup


class Post:
    def __init__(self, id,date,body,rating):
        self.id = id  # устанавливаем имя
        self.date = date  # устанавливаем имя
        self.body = body  # устанавливаем имя
        self.rating = rating  # устанавливаем имя



def scrape_data2(parentElement):
    list_of_posts = parentElement.find_all(class_='quote__frame')
    posti = list()
    for el in list_of_posts:
        post_id = el.find('a',class_='quote__header_permalink').text
        post_date = el.find('div',class_='quote__header_date').text
        post_body = el.find('div',class_='quote__body').text
        post_rating = el.find('div',class_='quote__total').text
        
        posti.append(Post(post_id,post_date,post_body,post_rating))
        
        print(post_id,post_date,post_body,post_rating)
    
    insert_to_database(posti)

def insert_to_database(post_array):
    try:
        connection = psycopg2.connect(user="ayaz",
                                  password="",
                                  host="",
                                  port="",
                                  database="")
        
        cursor = connection.cursor()

        postgres_insert_query = """SELECT public.add_unique_post(%s, %s, %s, %s) """
        for post in post_array:
            record_to_insert = (post.id[1:], post.date, post.body, post.rating)
            cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        eventLogger("Successfully added new posts to database")

    except (Exception, psycopg2.Error) as error :
        if(connection):
            eventLogger(error)

    finally:
        if(connection):
            cursor.close()
            connection.close()


def eventLogger(info):
    import win32api
    import win32con
    import win32evtlog
    import win32security
    import win32evtlogutil
    
    ph = win32api.GetCurrentProcess()
    th = win32security.OpenProcessToken(ph, win32con.TOKEN_READ)
    my_sid = win32security.GetTokenInformation(th, win32security.TokenUser)[0]
    
    applicationName = "Superior parser for BashIm"
    eventID = 4624
    category = 5	# Shell
    myType = win32evtlog.EVENTLOG_INFORMATION_TYPE
    descr = [info]
    data = "Application\0Data".encode("ascii")
    
    win32evtlogutil.ReportEvent(applicationName, eventID, eventCategory=category, 
        eventType=myType, strings=descr, data=data, sid=my_sid)

posts = list()
while(True):
    try:
        
        URL = "https://bash.im"
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, 'html.parser')
        time.sleep(5)
        scrape_data2(soup.find(class_='quotes'))
            

        eventLogger("Next scrap will start in 1 hour")
        time.sleep(3600)
        eventLogger("waited for 1 hour")
    except Exception as e:
        eventLogger(e)

