```
usage: reddit_sent [-c COMPANY] [-s SUBREDDITS] [-t TIME] [--dump-raw-data] [-h]
```

Determine general Reddit sentiment about a ticker. [Source: Reddit]

```
optional arguments:
  -c COMPANY, --company COMPANY
                        explicit name of company to search for, will override ticker symbol
  -s SUBREDDITS, --subreddits SUBREDDITS
                        comma deliminated string of subreddits to search, defaults to all
  -t TIME, --time TIME  time period to get posts from -- all, year, month, week, or day; defaults to day
  --dump-raw-data       displays all the raw data from reddit
  -h, --help            show this help message
```

Example:
```
2022 Mar 24, 15:24 (✨) /stocks/ba/ $ load AMC
2022 Mar 24, 15:26 (✨) /stocks/ba/ $ reddit_sent -s stocks,wallstreetbets -t week --dump-raw-data

This fricking white claw drinking smooth brain bought $AMC steadily through the past year or so. Most of my position though I got in Jan-March at the lower levels.

Sure AMC can say it's going to have its money invested in gold which is supposed to hedge against a crash or go up with some precious metals that company provide/source.

But Ry guy buying BBBY? Odd. Unless he makes them over to into some sort of online housewares version of amazon but better I don't get the move here.

I made two brackets comprised of the 64 most mentioned tickers on WallStreetBets over the last year. Over the next two weeks, these stocks will be matched up against each other on certain days, and their returns will determine who advances to the next round.

In one bracket, stocks with the higher daily return (measured from previous day's close) will advance. In the other bracket, the stocks with the highest daily loss will return.

Yes, I mean EVERY stock. I have just guaranteed that the entire stock market will 10x by the expiration of my calls. That means Tesla, AMC, Apple, that random penny stock you’ve been holding for a year, Nokia, and especially GameStop are finally going to print. All that HODLing is finally going to pay off for you guys. Buy my calls and they will print numbers you ain’t even heard of.

I know what you’re thinking… how is he going to pay at expiration? Don’t worry, I’m selling all of these calls on Robinhood after which I will delete the app and switch to Webull.

So, what I’m really trying to say is buy as much as you can now cause we’re in for a huge bull run. You guys can thank me later when you all get your lambos.

So I’m aware of the fact that $BB was caught in the whole WSB hype alongside GME and AMC. It was the only one of these 3 I invested in because I was under the impression that their QNX softwares were going to be used in many many cars manufactured in China and potentially later in the US. I heard that there were many quarter earnings with losses but that gains were going to be seen in the future. We’re almost a year removed from the actual WSB hype of $BB, and I’m just curious, now that all the smoke has settled, what are the realistic expectations for the stock (not the actual company itself even though I know there’s somewhat of a correlation)? Is it just going to hover around the $7-12 price point per share for a long time or is there possibly something in BB’s future that may trigger some more growth in the price?
```
