"""Reddit View"""
__docformat__ = "numpy"

import logging
import os
import warnings
from datetime import datetime
from typing import Dict

import finviz
import pandas as pd
import praw

import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from tqdm import tqdm
from typing import List

from gamestonk_terminal.common.behavioural_analysis import reddit_model
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def print_and_record_reddit_post(
    submissions_dict: Dict, submission: praw.models.reddit.submission.Submission
):
    """Prints reddit submission

    Parameters
    ----------
    submissions_dict : Dict
        Dictionary for storing reddit post information
    submission : praw.models.reddit.submission.Submission
        Submission to show
    """
    # Refactor data
    s_datetime = datetime.utcfromtimestamp(submission.created_utc).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    s_link = f"https://old.reddit.com{submission.permalink}"
    s_all_awards = "".join(
        f"{award['count']} {award['name']}\n" for award in submission.all_awardings
    )

    s_all_awards = s_all_awards[:-2]
    # Create dictionary with data to construct dataframe allows to save data
    submissions_dict[submission.id] = {
        "created_utc": s_datetime,
        "subreddit": submission.subreddit,
        "link_flair_text": submission.link_flair_text,
        "title": submission.title,
        "score": submission.score,
        "link": s_link,
        "num_comments": submission.num_comments,
        "upvote_ratio": submission.upvote_ratio,
        "awards": s_all_awards,
    }
    # Print post data collected so far
    console.print(f"{s_datetime} - {submission.title}")
    console.print(f"{s_link}")
    columns = ["Subreddit", "Flair", "Score", "# Comments", "Upvote %", "Awards"]
    data = [
        submission.subreddit,
        submission.link_flair_text,
        submission.score,
        submission.num_comments,
        f"{round(100 * submission.upvote_ratio)}%",
        s_all_awards,
    ]
    df = pd.DataFrame(data, columns=columns)
    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Reddit Submission"
    )
    console.print("\n")


@log_start_end(log=logger)
def display_watchlist(num: int):
    """Print other users watchlist. [Source: Reddit]

    Parameters
    ----------
    num: int
        Maximum number of submissions to look at
    """
    subs, d_watchlist_tickers, n_flair_posts_found = reddit_model.get_watchlists(num)
    for sub in subs:
        print_and_record_reddit_post({}, sub)
    if n_flair_posts_found > 0:
        lt_watchlist_sorted = sorted(
            d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True
        )
        s_watchlist_tickers = ""
        n_tickers = 0
        for t_ticker in lt_watchlist_sorted:
            try:
                # If try doesn't trigger exception, it means that this stock exists on finviz
                # thus we can print it.
                finviz.get_stock(t_ticker[0])
                if int(t_ticker[1]) > 1:
                    s_watchlist_tickers += f"{t_ticker[1]} {t_ticker[0]}, "
                n_tickers += 1
            except Exception:
                # console.print(e, "\n")
                pass
        if n_tickers:
            console.print(
                "The following stock tickers have been mentioned more than once across the previous watchlists:"
            )
            console.print(s_watchlist_tickers[:-2] + "\n")

    console.print("")


@log_start_end(log=logger)
def display_popular_tickers(
    n_top: int = 10, posts_to_look_at: int = 50, subreddits: str = "", export: str = ""
):
    """Print latest popular tickers. [Source: Reddit]

    Parameters
    ----------
    n_top : int
        Number of top tickers to get
    posts_to_look_at : int
        How many posts to analyze in each subreddit
    subreddits : str, optional
        String of comma separated subreddits.
    export : str
        Format to export dataframe
    """
    popular_tickers_df = reddit_model.get_popular_tickers(
        n_top, posts_to_look_at, subreddits
    )
    if not popular_tickers_df.empty:
        print_rich_table(
            popular_tickers_df,
            headers=list(popular_tickers_df.columns),
            show_index=False,
            title=f"\nThe following TOP {n_top} tickers have been mentioned:",
        )
    else:
        console.print("No tickers found")

    console.print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "popular",
        popular_tickers_df,
    )


@log_start_end(log=logger)
def display_spac_community(limit: int = 10, popular: bool = False):
    """Look at tickers mentioned in r/SPACs [Source: Reddit]

    Parameters
    ----------
    limit: int
        Number of posts to look through
    popular: bool
        Search by popular instead of new
    """
    subs, d_watchlist_tickers = reddit_model.get_spac_community(limit, popular)
    for sub in subs:
        print_and_record_reddit_post({}, sub)

    if d_watchlist_tickers:
        lt_watchlist_sorted = sorted(
            d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True
        )
        s_watchlist_tickers = ""
        n_tickers = 0
        for t_ticker in lt_watchlist_sorted:
            try:
                # If try doesn't trigger exception, it means that this stock exists on finviz
                # thus we can print it.
                finviz.get_stock(t_ticker[0])
                if int(t_ticker[1]) > 1:
                    s_watchlist_tickers += f"{t_ticker[1]} {t_ticker[0]}, "
                n_tickers += 1
            except Exception:
                # console.print(e, "\n")
                pass

        if n_tickers:
            console.print(
                "The following stock tickers have been mentioned more than once across the previous SPACs:"
            )
            console.print(s_watchlist_tickers[:-2])
    console.print("")


@log_start_end(log=logger)
def display_spac(limit: int = 5):
    """Look at posts containing 'spac' in top communities

    Parameters
    ----------
    limit: int
        Number of posts to get from each subreddit
    """
    warnings.filterwarnings("ignore")  # To avoid printing the warning
    subs, d_watchlist_tickers, n_flair_posts_found = reddit_model.get_spac(limit)
    for sub in subs:
        print_and_record_reddit_post({}, sub)

    if n_flair_posts_found > 0:
        lt_watchlist_sorted = sorted(
            d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True
        )
        s_watchlist_tickers = ""
        n_tickers = 0
        for t_ticker in lt_watchlist_sorted:
            try:
                # If try doesn't trigger exception, it means that this stock exists on finviz
                # thus we can print it.
                finviz.get_stock(t_ticker[0])
                if int(t_ticker[1]) > 1:
                    s_watchlist_tickers += f"{t_ticker[1]} {t_ticker[0]}, "
                n_tickers += 1
            except Exception:
                pass
        if n_tickers:
            console.print(
                "The following stock tickers have been mentioned more than once across the previous SPACs:"
            )
            console.print(s_watchlist_tickers[:-2])
    console.print("")


@log_start_end(log=logger)
def display_wsb_community(limit: int = 10, new: bool = False):
    """Show WSB posts

    Parameters
    ----------
    limit : int, optional
        Number of posts to look at, by default 10
    new : bool, optional
        Flag to sort by new instead of hot, by default False
    """
    subs = reddit_model.get_wsb_community(limit, new)

    for sub in subs:
        print_and_record_reddit_post({}, sub)


@log_start_end(log=logger)
def display_due_diligence(
    ticker: str, limit: int = 10, n_days: int = 3, show_all_flairs: bool = False
):
    """Display Reddit due diligence data for a given ticker

    Parameters
    ----------
    ticker: str
        Stock ticker
    limit: int
        Number of posts to get
    n_days: int
        Number of days back to get posts
    show_all_flairs: bool
        Search through all flairs (apart from Yolo and Meme)
    """
    subs = reddit_model.get_due_dilligence(ticker, limit, n_days, show_all_flairs)
    for sub in subs:
        print_and_record_reddit_post({}, sub)
    if not subs:
        console.print(f"No DD posts found for {ticker}\n")


@log_start_end(log=logger)
def display_reddit_graphic(
    search: str,
    time: str,
    graph_type: str,
    export: str = "",
    subreddits: List[str] = [
        "investing",
        "wallstreetbets",
        "stocks",
        "pennystocks",
        "GME",
        "robinhood",
    ],
):
    """Determine Reddit sentiment about a search term

    Parameters
    ----------
    search: str
        The term being search for in Reddit
    subreddits: str
        A comma deliminated string of subreddits to search through
    time: str
        A timeframe to limit the search to (all, year, month, week, day)
    dump_raw_data: bool
        Outputs raw search results to the terminal
    """
    posts = reddit_model.get_posts_about(
        subreddits=subreddits,
        search=search,
        time=time,
    )

    nltk.download("stopwords")
    tk = nltk.tokenize.RegexpTokenizer(r"\w+")
    stop_words = nltk.corpus.stopwords.words("english")
    blacklist = {"market", "stock", "company", "https", "imgur", "com", "stocks"}

    words = []

    console.print("")
    for post in tqdm(posts):
        ls_text = [post.selftext, post.title]
        post.comments.replace_more(limit=0)
        for comment in post.comments.list():
            ls_text.append(comment.body)

        tokens = tk.tokenize(" ".join(ls_text))
        for char in tokens:
            if char not in stop_words and char not in blacklist:
                words.append(char)

    if graph_type == "wordcloud":
        df = pd.Series(words)

        wc = WordCloud(width=1000, height=600, max_words=100, background_color="black")
        strcat = " ".join(word for word in words)
        wc.generate(strcat)

        plt.figure(figsize=(20, 10), facecolor="k")
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.show()
        console.print("")
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "reddit graphic",
            df,
        )
    elif graph_type == "histogram":
        df = pd.Series(words[0:20])
        df.value_counts().plot(kind="bar")
        console.print("")
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "reddit graphic",
            df,
        )
