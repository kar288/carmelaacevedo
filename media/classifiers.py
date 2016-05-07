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

now = datetime.datetime.now()
date = now.strftime('%Y-%m-%d')
time = now.strftime('%H-%M-%S')


def parse_docs_and_tags():
    titles = []
    ingredients = []
    preparations = []

    tags = []

    fname = sys.argv[1] if len(sys.argv) > 1 else './allrecipes.csv'
    with open(fname) as f:
        reader = csv.DictReader(f)
        for recipe in reader:
            titles.append(recipe['title'])
            ingredients.append(recipe['ingredients'])
            preparations.append(recipe['preparation'])

            tags.append(recipe['tags'])

    tfidf = TfidfVectorizer(max_features=1024)
    tfidf_prep = TfidfVectorizer(max_features=1024, stop_words='english')

    X_title = tfidf.fit_transform(titles).toarray()
    X_ingredients = tfidf.fit_transform(ingredients).toarray()
    X_preparation = tfidf_prep.fit_transform(preparations).toarray()

    counter = CountVectorizer(min_df=100, binary=True, tokenizer=str.split)
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

    X_title_tr, X_title_te, X_ingr_tr, X_ingr_te, \
        X_prep_tr, X_prep_te, y_tr, y_te = train_test_split(
            X_title, X_ingr, X_prep, y, train_size=.7)

    with tf.name_scope('Input_Merge'):
        title_input = Input(shape=(X_title.shape[1],), name='title_in')
        ingr_input = Input(shape=(X_ingr.shape[1],), name='ingr_in')
        prep_input = Input(shape=(X_prep.shape[1],), name='prep_in')

        X_input = merge([title_input, ingr_input, prep_input], mode='concat')

    with tf.name_scope('Dense_Hidden'):
        hidden = Dense(output_dim=512, activation='relu')(X_input)

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
        tsb = TensorBoard(
            log_dir=os.path.join('tensorboard', date, time),
            histogram_freq=1)

    feed_dict_tr = {
        'title_in': X_title_tr,
        'ingr_in': X_ingr_tr,
        'prep_in': X_prep_tr}

    feed_dict_te = {
        'title_in': X_title_te,
        'ingr_in': X_ingr_te,
        'prep_in': X_prep_te}

    model.fit(
        feed_dict_tr,
        y_tr,
        batch_size=50,
        nb_epoch=30,
        callbacks=[tsb],
        verbose=1,
        validation_data=(feed_dict_te, y_te))

    return model


def main():
    X, y, tags = parse_docs_and_tags()
    model = dnn(X, y)
    y_pred = model.predict([X[0], X[1], X[2]])

    print_tags(tags, y, y_pred)


if __name__ == "__main__":
    main()
