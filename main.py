# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging, ht

from flask import Flask, send_from_directory, redirect, url_for, render_template, request


app = Flask(__name__)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""

    return 'Hello World!'+ ht.execute()

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submitted', methods=['POST'])
def submitted_form():
    name = request.form['name']
    email = request.form['email']
    site = request.form['site_url']
    comments = request.form['comments']

    # [END submitted]
    # [START render_template]
    return render_template(
        'submitted_form.html',
        name=name,
        email=email,
        site=site,
        comments=comments)
    # [END render_template]
	
	
@app.route('/send')
def send():
    """Return a friendly HTTP greeting."""
    refreshData=False

    forceRefresh = request.args.get('forceRefresh')
    if "skadoosh" == forceRefresh:
        refreshData=True
    
    perDate = request.args.get('perDate')
    print("perDate "+str(perDate))
    print("forceRefresh "+str(forceRefresh))
    return send_from_directory(ht.execute(forceRefresh,perDate),"_summary.xlsx", as_attachment=True)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
