import nltk
from textblob import TextBlob
nltk.download('stopwords')

# conda install -c https://conda.anaconda.org/conda-forge wordcloud
def main():
    # TODO document dependencies
    txt = "MSFT is probably one of the last stocks you should be worried about. Perfect credit rating, beautiful balance sheet great revenue and profit. A tad pricey here but your not buying so that doesn’t matter as much. Probably one if the safest stocks out there with its massive moat and diversity"
    #txt = "MSFT is probably one of the last stocks you should be worried about. Perfect credit rating, beautiful balance sheet great revenue and profit. A tad pricey here but your not buying so that doesn’t matter as much. Probably one if the safest stocks out there with its massive moat and diversity"
    # tokenize and remove punctuation
    tk = nltk.tokenize.RegexpTokenizer(r"\w+")
    tokens = tk.tokenize(txt)

    stop_words = nltk.corpus.stopwords.words('english')

    words = [char for char in tokens if char not in stop_words]

    print(''.join(words))
    print(TextBlob(''.join(words)).sentiment.polarity)

if __name__ == "__main__":
    main()