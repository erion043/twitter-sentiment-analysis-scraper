# twitter-sentiment-analysis-scraper
A Twitter sentiment analysis tool, that scrapes and analyses tweets from the search tab of a certain topic.

### Arguments
-e, --email | Twitter email address | REQUIRED
-u, --username | Twitter username | REQUIRED
-p, --password | Twitter password | REQUIRED
-t, --topic | Topic to search for | REQUIRED
-n, --tweets_num | Number of tweets to scrape | DEFAULT = 100
-m, --sentiment_model | Pick sentiment model ("vader" or "roberta") |  DEFAULT = "vader"
-x, --csv_name | CSV output file name | DEFAULT = "output"
-r, --show_browser | Show browser window | FLAG
-c, --custom_csv | Analyze custom csv | DEFAULT = ""
-s, --save_without_html | Scrape and analyze the tweets without HTML escape tags (This won't launch the interface) | FLAG
-l, --port_number | Host on entered port | DEFAULT = 5000

#### Example
This example collects and analyses the top 500 tweets about the stock market.

```console
$ python sentiment_script.py -e <EMAIL> -u <USERNAME> -p <PASSWORD> -t "stock market" -n 500
```

### Common issues to look out for
1. If there's something wrong with scraping the tweets, it's likely due to limitations set by Twitter or a weak internet connection. If it's **really** not working, run the script with the -r flag to see what's going on and spot anything that needs fixing. You can open an issue if something needs fixing.
```console
$ python sentiment_script.py -e <EMAIL> -u <USERNAME> -p <PASSWORD> -t "stock market" -n 500 -r
```

2. If the interface doesn't load properly, then refresh the page. Often the page loads properly on the second refresh. If it doesn't load correctly after around five, then maybe there's an issue that would be helpful to report.
