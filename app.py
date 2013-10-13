from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from random import choice
import requests

client = MongoClient('localhost', 27017)
db = client.votedb
col = db['votes']

app = Flask(__name__)
app.debug = True


@app.route('/', methods=['GET', 'POST'])
def index():

    # If it's a GET request (someone is requesting data from this URL)
    # return a form with hot or not options
    if request.method == 'GET':

        # get my rising tech terms
        r = requests.get('https://chartbeat.com/labs/rising/topterms/'
                         '?host=chartbeat.com&apikey=1&tz=-240&_src=cb_dash')
        json = r.json()
        terms = [' '.join(term['grams'])
                 for term in json['data']['top_terms']['technology']]

        # pass along the tech terms in the terms variable to the template
        return render_template('vote.html', terms=terms)

    # If it's a POST request (someone is sending datat to this URL) store the
    # data in mongodb
    elif request.method == 'POST':
        for term, result in request.form.iteritems():
            counter = col.find_one({'term': term})
            if not counter:
                counter = {
                    'term': term,
                    'hot': 0,
                    'not': 0,
                }
            if result == 'hot':
                counter['hot'] += 1
            else:
                counter['not'] += 1

            # If update or insert a document where the term field matches term
            col.update({'term': term}, counter, upsert=True)

            # redirect to the results page
            return redirect(url_for('results'))


@app.route('/results')
def results():
    # find all the votes in the votes column of the database
    votes = col.find()

    # pass along the votes in the votes variable to the template
    return render_template('results.html', votes=votes)


if __name__ == '__main__':
    app.run()
