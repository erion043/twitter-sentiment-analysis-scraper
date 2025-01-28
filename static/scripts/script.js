let batch_num = 0;

function fetchData() {
    fetch('/get_data')
        .then((response) => response.json())
        .then((data) => {
            updatePieChart(data.chart_data, data.chart_labels);

            const pos = document.getElementById('pos');
            const neg = document.getElementById('neg');
            const neu = document.getElementById('neu');

            pos.innerHTML = '';
            neg.innerHTML = '';
            neu.innerHTML = '';

            let activeTabID = 'pos';
            let positiveTweets = data.tweet_data.positive;
            let negativeTweets = data.tweet_data.negative;
            let neutralTweets = data.tweet_data.neutral;

            let batch_num = 0;

            function loadTweets(container, tweets, batchSize = 2) {
                if (tweets.length === 0) return;

                batch_num += 1;
                const batchDiv = document.createElement('div');
                batchDiv.id = `batch${batch_num}`;
                batchDiv.classList.add('tweet-batch');
                batchSize = Math.min(batchSize, tweets.length);

                const toLoad = tweets.splice(0, batchSize);
                batchDiv.innerHTML = toLoad.join('<br>');

                container.appendChild(batchDiv);

                twttr.widgets.load(batchDiv);
            }

            loadTweets(pos, positiveTweets);
            loadTweets(neg, negativeTweets);
            loadTweets(neu, neutralTweets);

            const posTabButton = document.getElementById('pos-butt');
            const negTabButton = document.getElementById('neg-butt');
            const neuTabButton = document.getElementById('neu-butt');

            posTabButton.addEventListener('click', () => {
                activeTabID = 'pos';
                pos.style.display = 'block';
                neg.style.display = 'none';
                neu.style.display = 'none';
            });

            negTabButton.addEventListener('click', () => {
                activeTabID = 'neg';
                pos.style.display = 'none';
                neg.style.display = 'block';
                neu.style.display = 'none';
            });

            neuTabButton.addEventListener('click', () => {
                activeTabID = 'neu';
                pos.style.display = 'none';
                neg.style.display = 'none';
                neu.style.display = 'block';
            });

            const tweetsContainer = document.getElementById('scroller');

            tweetsContainer.addEventListener("scroll", () => {
                const threshold = 5;

                if (
                    tweetsContainer.scrollTop + tweetsContainer.clientHeight >=
                    tweetsContainer.scrollHeight - threshold
                ) {
                    if (activeTabID === 'pos' && positiveTweets.length > 0) {
                        loadTweets(pos, positiveTweets);
                    } else if (activeTabID === 'neg' && negativeTweets.length > 0) {
                        loadTweets(neg, negativeTweets);
                    } else if (activeTabID === 'neu' && neutralTweets.length > 0) {
                        loadTweets(neu, neutralTweets);
                    }
                }
            });
        });
}

function loadTwitterScript() {
    const script = document.createElement('script');
    script.src = 'https://platform.twitter.com/widgets.js';
    script.async = true;
    script.charset = 'utf-8';
    document.body.appendChild(script);
}


function changeTab(tabId) {
    const tabs = document.querySelectorAll('.tab');
    const tweetContainers = document.querySelectorAll('.tweet-container');

    tabs.forEach(tab => tab.classList.remove('active-tab'));
    tweetContainers.forEach(tweet => tweet.style.display = 'none');

    document.querySelector(`[onclick="changeTab('${tabId}')"]`).classList.add('active-tab');
    document.getElementById(tabId).style.display = 'block';
}

function updatePieChart(data, labels) {
    const ctx = document.getElementById('pieChart').getContext('2d');
    const pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['green', 'red', 'yellow'],
                borderColor: ['darkgreen', 'darkred', 'darkyellow'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

function onLoadFunctions() {
    fetchData();
    loadTwitterScript();
}

window.onload = onLoadFunctions;