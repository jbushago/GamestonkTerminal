"""Reddit View"""
__docformat__ = "numpy"

import logging
import os
import warnings
from datetime import datetime
from typing import Dict, List

import finviz
import matplotlib.pyplot as plt
import pandas as pd
import praw
import seaborn as sns
from tqdm import tqdm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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
def display_reddit_sent(
    ticker: str,
    sort: str,
    limit: int,
    time_frame: str,
    full_search: bool,
    graphic: bool,
    dump_raw_data: bool = False,
    export: str = "",
):
    """Determine Reddit sentiment about a search term

    Parameters
    ----------
    ticker: str
        The ticker being search for in Reddit
    sort: str
        Type of search
    time_frame: str
        time frame for search
    full_search: bool
        enable comprehensive search for ticker
    limit: str
        Number of
    dump_raw_data: bool
        Outputs raw search results to the terminal
    """

    posts = reddit_model.get_posts_about(ticker, limit, sort, time_frame)
    post_data = []
    compound_scores = []

    columns = ["Title", "pos", "neu", "neg", "compound"]

    if not posts:
        console.print(f"No posts for {ticker} found")
        return

    console.print(f"Found {len(posts)} submissions")
    console.print("Analyzing each post...")
    for p in tqdm(posts):
        texts = [p.title, p.selftext]
        if full_search:
            tlcs = reddit_model.get_comments(p)
            texts.extend(tlcs)
        preprocessed_text = reddit_model.clean_reddit_text(texts)
        # console.print(preprocessed_text)
        analyzer = SentimentIntensityAnalyzer()
        sentiment = analyzer.polarity_scores(preprocessed_text)
        positive_score = sentiment["pos"]
        neutral_score = sentiment["neu"]
        negative_score = sentiment["neg"]
        compound_score = sentiment["compound"]
        # corpus_blob = TextBlob(preprocessed_text)
        # sentiment = corpus_blob.sentiment
        # polarity_score = sentiment.polarity
        # subjectivity_score = sentiment.subjectivity
        compound_scores.append(compound_score)
        post_data.append(
            [p.title, positive_score, neutral_score, negative_score, compound_score]
        )

    avg_score = sum(compound_scores) / len(compound_scores)

    df = pd.DataFrame(post_data, columns=columns)
    if dump_raw_data:
        print_rich_table(
            df, headers=list(df.columns), show_index=False, title="Sentiment Debug Dump"
        )
    if graphic:
        display_box_whisker(ticker, compound_scores)

    console.print(f"\nSentiment score for {ticker} is {avg_score}\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"{ticker}_sentiment",
        df,
    )


@log_start_end(log=logger)
def display_box_whisker(ticker: str, scores: List[float]):
    """Display box and whisker plot for sentiment scores of each post

    Parameters
    ----------
    ticker: str
        ticker symbol
    scores: List[float]
        sentiment scores of each post
    """
    boxplot = sns.boxplot(x=scores)
    boxplot.set(title=f"Sentiment Score of Submissions for {ticker}")
    plt.xlabel("Sentiment Scores")
