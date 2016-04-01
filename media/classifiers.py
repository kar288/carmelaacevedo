import csv
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from keras.callbacks import TensorBoard
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.layers.core import Activation, Dense, Dropout, Flatten
from keras.models import Sequential
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import (precision_recall_curve,
                             precision_recall_fscore_support)
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import normalize
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
                    recipe['ingredients']]))
                    # recipe['preparation']]))

    tfidf = TfidfVectorizer(stop_words='english', min_df=100)
    X = tfidf.fit_transform(docs).toarray()

    counter = TfidfVectorizer(min_df=100, tokenizer=str.split)
    y = normalize(counter.fit_transform(tags).toarray(), norm='l1')

    n_labels = y.shape[1]
    tag_index = {idx: tag for tag, idx in counter.vocabulary_.items()}
    tags = np.asarray([tag_index[i] for i in range(n_labels)])

    return X, y, tags


def classify(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=.7)
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
            print(', '.join(tags[y_true[i] != 0.0]), file=f)


def dnn(X_train, X_test, y_train, y_test):
    n_words, n_tags = X_train.shape[1], y_train.shape[1]
    model = Sequential()

    with tf.name_scope('Dense_Hidden'):
        model.add(Dense(output_dim=1024, input_dim=n_words))
        model.add(Activation('relu'))

    with tf.name_scope('Dropout'):
        model.add(Dropout(p=0.5))

    with tf.name_scope('Dense_Out'):
        model.add(Dense(n_tags))
        model.add(Activation('softmax'))

    with tf.name_scope('Optimize_Model'):
        model.compile(loss='categorical_crossentropy', optimizer='sgd')

    # tsb = TensorBoard(
    #     log_dir=os.path.join(self.out_dir, 'model'),
    #     histogram_freq=1)

    with tf.name_scope('Fit_Model'):
        model.fit(
            X_train,
            y_train,
            batch_size=50,
            nb_epoch=10,
            verbose=1,
            validation_data=(X_test, y_test))

    return model.predict_proba(X_test)


def main():
    X, y, tags = parse_docs_and_tags('./allrecipes.csv')
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=.7)
    y_pred = dnn(X_train, X_test, y_train, y_test)
    print_tags(tags, y_test, y_pred)


if __name__ == "__main__":
    main()
