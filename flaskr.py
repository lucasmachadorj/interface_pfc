# coding: utf-8

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import preprocessing
import os


app = Flask(__name__, template_folder='template', static_folder='static', static_url_path='/static')
app.config['DEBUG'] = True
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

some_engine = create_engine('postgresql://postgres:248091-Jr@localhost/pfc')
Session = sessionmaker(bind=some_engine)
session = Session()

UPLOAD_FOLDER = './netflow/'
ALLOWED_EXTENSIONS = set(['binetflow', 'csv'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class Diagnostics(db.Model):

    __tablename__ = 'bot_diagnostics'

    id = db.Column('id', db.Integer, primary_key=True)
    addr = db.Column('addr', db.Integer)
    model = db.Column('model', db.String(100))
    date = db.Column('date', db.Date)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        data = json.loads(request.data)
        model = data['model']
        date = data['date']
        ip = data['ip']
        print(date)
        if model and date and ip:
            values = Diagnostics.query.filter_by(addr=ip, model=model, date=date).all()
        elif model and date:
            values = Diagnostics.query.filter_by(model=model, date=date).all()
        elif model and ip:
            values = Diagnostics.query.filter_by(model=model, addr=ip).all()
        elif ip and date:
            values = Diagnostics.query.filter_by(addr=ip, date=date).all()
        elif ip:
            values = Diagnostics.query.filter_by(addr=ip).all()
        elif model:
            values = Diagnostics.query.filter_by(model=model).all()

        else:
            if date:
                values = Diagnostics.query.filter_by(date=date).all()
            else:
                values = Diagnostics.query.all()

        results = []
        for value in values:
            result = {}
            result['addr'] = value.addr.strip()
            result['model'] = value.model.strip()
            result['date'] = str(value.date).strip()
            results.append(result)

        return json.dumps(results)
    else:
        pass

@app.route('/statistics', methods=['GET', 'POST'])
def statistics():
    if request.method == 'POST':
        data = json.loads(request.data)
        date = data['date']
        if date:
            values = session.query(Diagnostics.model, func.count('addr').label('ataques')).filter(Diagnostics.date == date).group_by(Diagnostics.model);
            results = []
            for value in values:
                result = {}
                result['model'] = value.model.strip()
                result['ataques'] = value.ataques
                results.append(result)
            return json.dumps(results)

    else:
        return render_template('statistics.html')


@app.route('/loadnetflow', methods=['GET', 'POST'])
def load_netflow():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            ip = request.form['ip']
            port = request.form['port']
            username = request.form['username']
            password = request.form['password']
            dbname = request.form['dbname']
            if not (ip and username and password and dbname):
                return redirect(request.url)
            else:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                preprocessing.save_netflow(ip, port, username, password, dbname)
                return redirect('/classify')
    else:
        return render_template('loadnetflow.html')

@app.route('/classify', methods=['GET', 'POST'])
def classify():
    if request.method == 'POST':
        ip = request.form['ip']
        port = request.form['port']
        username = request.form['username']
        password = request.form['password']
        if not (ip and port and username and password):
            return redirect(request.url)
        else:
            preprocessing.preprocessor(ip, port, username, password)
            return redirect(request.url)
    else:
        return render_template('classify.html')

if __name__ == '__main__':
    app.run()
