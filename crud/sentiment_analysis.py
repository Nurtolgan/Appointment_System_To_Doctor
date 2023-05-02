from textblob import TextBlob
from textblob.classifiers import NaiveBayesClassifier
from textblob import TextBlob
from textblob.sentiments import PatternAnalyzer


testimonial = TextBlob("Good doc! big thx")
print(testimonial.sentiment)
print(testimonial.sentiment.polarity)