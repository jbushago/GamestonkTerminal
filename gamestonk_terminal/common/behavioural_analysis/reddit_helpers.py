"""Reddit Helpers"""
__docformat__ = "numpy"

from typing import List
import re

import praw

def find_all_body_tickers(ls_text: List[str]) -> List[str]:
    l_tickers_found = []
    for s_text in ls_text:
        print("s_text == "+s_text)
        for s_ticker in set(re.findall(r'(?<=\$)\w+|[A-Z]{3,6}', s_text)):
            print(s_ticker)
            l_tickers_found.append(s_ticker.strip())

    return l_tickers_found

def find_tickers(submission: praw.models.reddit.submission.Submission) -> List[str]:
    """Extracts potential tickers from reddit submission

    Parameters
    ----------
    submission : praw.models.reddit.submission.Submission
        Reddit post to scan

    Returns
    -------
    List[str]
        List of potential tickers
    """
    ls_text = [submission.selftext, submission.title]
    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list():
        ls_text.append(comment.body)

    return find_all_body_tickers(ls_text)
