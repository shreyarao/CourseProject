from functools import partial
from flask import Flask, render_template, jsonify, request
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import requests
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import re
import sys
from newsapi import NewsApiClient
from werkzeug.wrappers import response

app = Flask(__name__)

@app.route('/get_top_results', methods=['POST'])
def get_top_results():

    # get documents
    r1 = requests.get("https://apnews.com/hub/us-news?utm_source=apnewsnav&utm_medium=navigation")
    coverpage = r1.content
    soup1 = BeautifulSoup(coverpage, 'html5lib')

    regex = re.compile('.*Component-headline-.*')
    regex2 = re.compile('.*Component-root-.*')
    coverpage_news = soup1.find_all('a', class_=regex)
    documents = []
    for i in range(0, len(coverpage_news)):
        link = coverpage_news[i]['href']
        article = requests.get("https://apnews.com/"+link)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')
        body = soup_article.find_all('p', class_=regex2)
        
        list_paragraphs = []
        final_article = ""
        for j in np.arange(0, len(body)):
            paragraph = body[j].get_text()
            list_paragraphs.append(paragraph)
            final_article = " ".join(list_paragraphs)
            final_article = final_article.strip('"')
            final_article = final_article.strip('\n')

        documents.append(final_article)

    # tf-idf
    def pre_process(text):
        text=text.lower()
        text=re.sub("</?.*?>"," <> ",text)
        text=re.sub("(\\d|\\W)+"," ",text)
        return text

    documents = list(map(pre_process, documents))

    def get_stop_words(stop_file_path):
        with open(stop_file_path, 'r', encoding="utf-8") as f:
            stopwords = f.readlines()
            stop_set = set(m.strip() for m in stopwords)
            return frozenset(stop_set)

    #load a set of stop words
    stopwords=get_stop_words("stopwords.txt")

    cv=CountVectorizer(max_df=0.85,stop_words=stopwords)
    word_count_vector=cv.fit_transform(documents)
    

    tfidf_transformer=TfidfTransformer(smooth_idf=True,use_idf=True)
    tfidf_transformer = tfidf_transformer.fit(word_count_vector)


    def sort_coo(coo_matrix):
        tuples = zip(coo_matrix.col, coo_matrix.data)
        return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)

    def extract_topn_from_vector(feature_names, sorted_items, topn=10):
    
        #use only topn items from vector
        sorted_items = sorted_items[:topn]

        score_vals = []
        feature_vals = []

        for idx, score in sorted_items:
            fname = feature_names[idx]
            
            #keep track of feature name and its corresponding score
            score_vals.append(round(score, 3))
            feature_vals.append(feature_names[idx])

        #create a tuples of feature,score
        #results = zip(feature_vals,score_vals)
        results= {}
        for idx in range(len(feature_vals)):
            results[feature_vals[idx]]=score_vals[idx]
        
        return results

    feature_names=cv.get_feature_names()

    # get the document that we want to extract keywords from
    content = request.json
    doc = content['body'].strip('\n')

    #generate tf-idf for the given document
    tf_idf_vector=tfidf_transformer.transform(cv.transform([doc]))

    #sort the tf-idf vectors by descending order of scores
    sorted_items=sort_coo(tf_idf_vector.tocoo())

    #extract only the top n; n here is 10
    keywords=extract_topn_from_vector(feature_names,sorted_items,3)

    # use bing api with query from tf-idf
    keyword_string = ""
    for k in keywords:
        print(k,sys.stderr)
        print(keywords[k], sys.stderr)
        keyword_string = keyword_string + k + " AND "

    keyword_string = keyword_string[:-4]
    print(keyword_string, sys.stderr)

    headlines = requests.get("https://newsapi.org/v2/everything?q="+keyword_string+"&from=2021-11-10&sortBy=popularity&apiKey=c076670072e640d097b0e4d80f70257c")
    return headlines.content

if __name__ == "__main__":
    app.run(debug=True)