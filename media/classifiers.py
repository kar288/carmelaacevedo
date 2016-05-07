import csv
import datetime
import os
import sys

import numpy as np
import tensorflow as tf
from keras.callbacks import TensorBoard
from keras.layers import Dense, Dropout, Input, merge
from keras.models import Model
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB


def parse_docs_and_tags():
    titles = []
    ingredients = []
    preparations = []

    tags = []

    reader = csv.DictReader(sys.stdin)
    for recipe in reader:
        titles.append(recipe['title'])
        ingredients.append(recipe['ingredients'])
        preparations.append(recipe['preparation'])

        tags.append(recipe['tags'])

    tfidf = TfidfVectorizer(max_features=5000)
    tfidf_prep = TfidfVectorizer(max_features=5000, stop_words='english')

    X_title = tfidf.fit_transform(titles).toarray()
    X_ingredients = tfidf.fit_transform(ingredients).toarray()
    X_preparation = tfidf_prep.fit_transform(preparations).toarray()

    counter = CountVectorizer(min_df=1, binary=True, tokenizer=str.split)
    y = counter.fit_transform(tags).toarray()

    n_labels = y.shape[1]
    tag_index = {idx: tag for tag, idx in counter.vocabulary_.items()}
    tags = np.asarray([tag_index[i] for i in range(n_labels)])

    return (X_title, X_ingredients, X_preparation), y, tags


def classify(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=.7)
    classifier = MultinomialNB()
    y_score = OneVsRestClassifier(classifier).fit(
        X_train, y_train).predict_proba(X)

    return y, y_score


def print_tags(tags, y_true, y_pred):
    # idx = np.argsort(y_pred, axis=1)
    with open('./tags.out', 'w') as f:
        for i in range(y_pred.shape[0]):
            print(', '.join(list(tags[y_pred[i] > 0.5])), file=f)

    with open('./truth.out', 'w') as f:
        for i in range(y_true.shape[0]):
            print(', '.join(tags[y_true[i] != 0.0]), file=f)


def dnn(X, y):
    X_title, X_ingr, X_prep = X

    with tf.name_scope('Input_Merge'):
        title_input = Input(shape=(X_title.shape[1],), name='title_in')
        ingr_input = Input(shape=(X_ingr.shape[1],), name='ingr_in')
        prep_input = Input(shape=(X_prep.shape[1],), name='prep_in')

        X_input = merge([title_input, ingr_input, prep_input], mode='concat')

    with tf.name_scope('Dense_Hidden'):
        hidden = Dense(output_dim=4096, activation='relu')(X_input)

    with tf.name_scope('Dropout'):
        dropout = Dropout(p=0.5)(hidden)

    with tf.name_scope('Dense_Out'):
        out = Dense(output_dim=y.shape[1], activation='sigmoid')(dropout)

    with tf.name_scope('Optimize_Model'):
        model = Model(input=[title_input, ingr_input, prep_input], output=out)
        model.compile(
            loss='binary_crossentropy',
            optimizer='SGD',
            metrics=['accuracy'])

    with tf.name_scope('Fit_Model'):
        now = datetime.datetime.now()
        date = now.strftime('%Y-%m-%d')
        time = now.strftime('%H-%M-%S')

        tsb = TensorBoard(
            log_dir=os.path.join('tensorboard', date, time),
            histogram_freq=1)

    feed_dict = {'title_in': X_title, 'ingr_in': X_ingr, 'prep_in': X_prep}
    model.fit(
        feed_dict,
        y,
        batch_size=50,
        nb_epoch=30,
        callbacks=[tsb],
        verbose=1,
        validation_split=0.7)

    return model.predict(feed_dict)


def main():
    X, y, tags = parse_docs_and_tags()
    y_pred = dnn(X, y)
    print_tags(tags, y, y_pred)


if __name__ == "__main__":
    main()
