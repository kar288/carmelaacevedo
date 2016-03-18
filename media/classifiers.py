import csv
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import (precision_recall_curve,
                             precision_recall_fscore_support)
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC


def plot_precision_recall(precision, recall):
    plt.clf()
    plt.plot(recall, precision, label='Precision-recall curve')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall curve')
    plt.show()


def parse_docs_and_tags(fname):
    docs = []
    tags = []

    with open(fname) as recipes:
        reader = csv.DictReader(recipes)
        for line_no, recipe in enumerate(reader):
            tags.append(recipe['tags'])
            docs.append(
                ' '.join([
                    recipe['title'],
                    recipe['ingredients'],
                    recipe['preparation']]))

    tfidf = TfidfVectorizer(stop_words='english')
    X = tfidf.fit_transform(docs)

    binary = CountVectorizer(binary=True, min_df=100, tokenizer=str.split)
    y = binary.fit_transform(tags).toarray()

    n_labels = y.shape[1]
    tag_index = {idx: tag for tag, idx in binary.vocabulary_.items()}
    tags = np.asarray([tag_index[i] for i in range(n_labels)])

    return X, y, tags


def classify(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.7)
    classifier = MultinomialNB()
    y_score = OneVsRestClassifier(classifier).fit(
        X_train, y_train).predict_proba(X)

    return y, y_score


def print_tags(tags, y_true, y_pred):
    idx = np.argsort(y_pred, axis=1)
    with open('./tags.out', 'w') as f:
        for i in range(y_pred.shape[0]):
            print(', '.join(list(tags[idx[i, -5:]])), file=f)

    with open('./truth.out', 'w') as f:
        for i in range(y_true.shape[0]):
            print(', '.join(tags[y_true[i] == 1]), file=f)


def main():
    X, y, tags = parse_docs_and_tags('./allrecipes.csv')
    y_true, y_pred = classify(X, y)
    print_tags(tags, y_true, y_pred)


if __name__ == "__main__":
    main()
