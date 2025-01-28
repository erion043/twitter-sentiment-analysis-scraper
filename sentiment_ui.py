from flask import Flask, render_template, jsonify
import pandas as pd
import re
import webbrowser
import threading

app = Flask(__name__)

def seperate_txt_med(text):
    result = ["", ""]
    
    links = re.findall(r"https://t\.co/([a-zA-Z0-9]+)", text)
    
    if links:
        url_id = links[-1]
        final_handle = f'<a href="https://t.co/{url_id}">pic.twitter.com/{url_id}</a>'
        result[1] = final_handle
        
        text = re.sub(r"https://t\.co/[a-zA-Z0-9]+", "", text).strip()
    
    result[0] = text
    return result

def embed_list(df):
    result = {
        'positive': [],
        'negative': [],
        'neutral' : []
    }
    for index, row in df.iterrows():
        context = seperate_txt_med(row["Text"])
        embed_str = f"""
        <div class="tweet-divs">
        <blockquote class="twitter-tweet">
        <p lang="en" dir="ltr">{context[0]}{context[1]}</p>
        &mdash; {row['Username']} (@{row['User_Handle']}) 
        <a href="{row['URL']}">{months[row['Timestamp'][4:7]]} {row['Timestamp'][8:10]}, {row['Timestamp'][-4:]}</a>
        </blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
        <div style="margin-left: 20px, margin-top: 50%">
            <h1>{row['Compound_Sentiment']}</h1>
            <h3>{"This tweet contains<br>media which wasn't analysed.<br>Its classification might be incorrect." if row['Media'] else ""}</h3>
        </div>
        </div>
        """

        if row['Compound_Sentiment'] >= 0.3:
            result['positive'].append(embed_str)
        elif row['Compound_Sentiment'] <= -0.3:
            result['negative'].append(embed_str)
        else:
            result['neutral'].append(embed_str)
        
    return result

months = {
    'Jan': 'January',
    'Feb': 'February',
    'Mar': 'March',
    'Apr': 'April',
    'May': 'May',
    'Jun': 'June',
    'Jul': 'July',
    'Aug': 'August',
    'Sep': 'September',
    'Oct': 'October',
    'Nov': 'November',
    'Dec': 'December'
}

def display_csv(csv_path,port):
    df = pd.read_csv(csv_path)


    tweet_data = embed_list(df)
    data = {
        "tweet_data": tweet_data,
        "chart_data": [len(tweet_data['positive']), len(tweet_data['negative']), len(tweet_data['neutral'])],  # Example data for the pie chart
        "chart_labels": ["Positive", "Negative", "Neutral"]
    }
    

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/get_data', methods=['GET'])
    def get_data():
        data_to_send = data  # Retrieve the data
        return jsonify(data_to_send)  # Return data as JSON

    host = '127.0.0.1'

    def host_page():
        app.run(host=host, port=port)
    ui = threading.Thread(target=host_page)

    webbrowser.open(f"http://{host}:{port}")
    ui.start()