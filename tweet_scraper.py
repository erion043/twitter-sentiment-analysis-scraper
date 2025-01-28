from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError
import time
import csv
import requests
import os
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
import html

def scrape_tweets(email: str, username: str, password: str, topic:str, des_num: int, csv_name:str = "output", headless:bool=True, html_friendly:bool = True) -> str:
    
    script_directory = os.path.dirname(os.path.abspath(__file__))
    if '.' in csv_name:
        print("'.' character is not allowed as csv filename")
        raise Exception
    path = f'{script_directory}/{csv_name}.csv'

    _xhr_calls = []
    tweets_data = []

    def intercept_response(response):
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response
    
    with sync_playwright() as pw:
        #launching the browser
        browser = pw.chromium.launch(headless=headless)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        session = context.new_page()
        session.goto("https://x.com/explore")
        
        #logging in
        print("Attempting to Sign in")
        session.fill('input[type="text"]', username)
        session.get_by_text('Next').click()
        password_field = session.locator('input[type="password"]')
        time.sleep(1)

        if not password_field.is_visible():
            session.fill('input[type="text"]', email)
            session.get_by_text('Next').click()

        password_field.fill(password)
        session.get_by_text('Log in').click()
        time.sleep(3)

        if 'login' in session.url:
            print('Log in Successful!')
        else:
            raise Exception
        
        #setting up .csv file
        file = open(path, "w", newline='', encoding='utf-8')
        writer = csv.writer(file)
        writer.writerow(["ID", "URL", "Username", "User_Handle","Text", "Likes", "Retweets", "Verified", "Timestamp", "Media"])

        #searching for tweets
        print(f'Searching for "{topic}"')
        session.fill('input[placeholder="Search"]', topic)
        session.keyboard.press('Enter')
        
        

        #listen for xhr calls
        session.on("response", intercept_response)

        #queriying tweets, intercepting xhr calls, and writting the content in a csv
        print(f'Attempting to gather {des_num} tweets about: "{topic}"')
        
        scraped_num = 0
        
        while scraped_num < des_num:
            tweets_call = None
            try:
                while tweets_call == None:
                    retry_attempts = 10
                    session.wait_for_selector('article[data-testid="tweet"]')

                    retry_button_locator = session.locator("button:has-text('Retry')")
                    while retry_button_locator.is_visible() and retry_attempts != 0:
                        retry_button_locator.click()
                        time.sleep(2)
                        retry_attempts -= 1

                    for f in _xhr_calls:
                        if "SearchTimeline" in f.url:
                            tweets_call = f
                            _xhr_calls.clear()
                            break

                    _xhr_calls.clear()        
                    session.evaluate('window.scrollBy(0, window.innerHeight)*5')
            except Exception:
                print(f"\rERROR: Timeout Occurred. CSV saved!")
                break

            data = None    
            try:
                data = tweets_call.json()
            except (requests.exceptions.JSONDecodeError, ValueError):
                print(f"\rERROR: JSON of request is not callable! CSV saved!")
                break
            
            try:
                timeline_data = data['data']['search_by_raw_query']['search_timeline']['timeline']['instructions'][0]['entries']
            except KeyError:
                print(timeline_data)
                break


            tweets_data = [tweet_object for tweet_object in timeline_data if "tweet" in tweet_object["entryId"]]

            for tweet in tweets_data:
                if scraped_num == des_num:
                    break
                try:
                    tweet_id = tweet["content"]["itemContent"]["tweet_results"]["result"]["rest_id"]
                    handle = tweet["content"]["itemContent"]["tweet_results"]["result"]["core"]["user_results"]["result"]["legacy"]["screen_name"]
                    url = f'https://twitter.com/{handle}/status/{tweet_id}'
                    name = tweet["content"]["itemContent"]["tweet_results"]["result"]["core"]["user_results"]["result"]["legacy"]["name"]
                    text = tweet["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["full_text"]
                    likes = tweet["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["favorite_count"]
                    retweets = tweet["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["retweet_count"]
                    verification = tweet["content"]["itemContent"]["tweet_results"]["result"]["core"]["user_results"]["result"]["is_blue_verified"]
                    timestamp = tweet["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["created_at"]
                    media = True if "extended_entities" in tweet["content"]["itemContent"]["tweet_results"]["result"]["legacy"] else False
    
                    if detect(text) == 'en':
                        if html_friendly:
                            text = html.escape(text, quote=True)
                            text = text.replace("\n", "<br>")
                        else:
                            text = text.replace("\n", " ")
                        writer.writerow([scraped_num, url, name, handle, text, likes, retweets, verification, timestamp, media])
                        scraped_num += 1

                except (KeyError, LangDetectException):
                    continue
            
            print(f'\rTweets scraped: {scraped_num}', end= "")
        
        file.flush()
        file.close()
        if scraped_num >= des_num:
            print(f'\rScraped gracefully with {scraped_num} scraped tweets')
        else:
            print(f'\rFinished scraping early with {scraped_num} scraped tweets')
        
        browser.close()
    return path