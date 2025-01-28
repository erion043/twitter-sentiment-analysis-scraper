from tweet_scraper import scrape_tweets
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax
import argparse
from sentiment_ui import display_csv
import string
import re
from html import unescape

def filter_text(text):
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Unescape HTML entities
    text = unescape(text)
    
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # Remove non-alphanumeric characters except spaces and punctuation
    return re.sub(r'[^a-zA-Z0-9\s' + re.escape(string.punctuation) + ']', '', text)

#Roberta
def analyse_all_roberta(df:pd.DataFrame) -> list:
    MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(MODEL,clean_up_tokenization_spaces=True)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)

    print('Analyzing with RoBERTa...')

    def polarity_scores(text: str):
        encoded_text = tokenizer(text, return_tensors='pt')
        output = model(**encoded_text)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        comp_result = (scores[2] - scores[0]) / ((scores[0] + scores[1] + scores[2]) + 1e-7)
        return comp_result

    result = []
    for idx, row in enumerate(df["Text"]):
        result.append(polarity_scores(filter_text(row)))
    return result


#VADER
def analyse_all_vader(df:pd.DataFrame) -> list:
    nltk.download('vader_lexicon')

    print('Analyzing with VADER...')

    sia = SentimentIntensityAnalyzer()
    def comp_polarity(text: str) -> int:
        return sia.polarity_scores(text)['compound']
    
    result = []
    for row in df["Text"]:
        result.append(comp_polarity(filter_text(row)))
    return result

def parse_args():
    parser = argparse.ArgumentParser(description="Scrape and analyze tweets sentiment")
    parser.add_argument('-e', '--email', type=str, required=True, help='Twitter email address')
    parser.add_argument('-u', '--username', type=str, required=True, help='Twitter username')
    parser.add_argument('-p', '--password', type=str, required=True, help='Twitter password')
    parser.add_argument('-t', '--topic', type=str, required=True, help='Topic to search for')
    parser.add_argument('-n', '--tweets_num', type=int, default=100, help='Number of tweets to scrape')
    parser.add_argument('-m', '--sentiment_model', type=str, default='vader', help='Pick sentiment model ("vader" or "roberta")')
    parser.add_argument('-x', '--csv_name', type=str, default='output', help='CSV output file name')
    parser.add_argument('-r', '--show_browser', action='store_false', help='Show browser window')
    parser.add_argument('-c', '--custom_csv', type=str, default="", help="Analyse custom csv")
    parser.add_argument('-s', '--save_without_html', action='store_false',help='Scrape and analyse the tweets without html escape tags (This wont launch the interface)' )
    parser.add_argument('-l', '--port_number', type=int, default=5000, help='Host on entered port')

    return parser.parse_args()

def main():
    args = parse_args()

    csv_path = scrape_tweets(args.email, args.username, args.password, args.topic, args.tweets_num, args.csv_name, args.show_browser, args.save_without_html) if args.custom_csv == "" else args.custom_csv
    df = pd.read_csv(csv_path)

    if "Compound_Sentiment" not in df.columns:
        if args.sentiment_model == 'roberta':
            df['Compound_Sentiment'] = analyse_all_roberta(df)
        else:
            df['Compound_Sentiment'] = analyse_all_vader(df)
        df.to_csv(csv_path, index=False)
    else:
        print("csv already analysed")

    if args.save_without_html:
        display_csv(csv_path, args.port_number)


if __name__ == "__main__":
    main()
    