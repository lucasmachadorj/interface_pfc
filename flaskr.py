# coding: utf-8

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Date, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
from sqlalchemy import or_, and_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import preprocessing
import os


app = Flask(__name__, template_folder='template', static_folder='static', static_url_path='/static')
app.config['DEBUG'] = True
Base = declarative_base()

global_session = 0

UPLOAD_FOLDER = './netflow/'
ALLOWED_EXTENSIONS = set(['binetflow', 'csv'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class Diagnostics(Base):

    __tablename__ = 'bot_diagnostics'

    id = Column('id', Integer, primary_key=True)
    addr = Column('addr', Integer)
    model = Column('model', String(100))
    date = Column('date', Date)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():

    if request.method == 'POST':
        try:
            data = json.loads(request.data)

            connip = data['connip']
            port = data['port']
            username = data['username']
            password = data['password']
            dbname = data['dbname']

            model = data['model']
            date = data['date']
            endDate = data['endDate']
            ip = data['ip']
            conn = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(username, password, connip, port, dbname)
            some_engine = create_engine(conn)
            Session = sessionmaker(bind=some_engine)
            session = Session()
            global_session = session
        except:
            render_template('index.html')


        if model and date and ip and endDate:
            values = session.query(Diagnostics).filter(date>=date).filter(date<=endDate).filter_by(addr=ip, model=model).all()
        elif model and date and endDate:
            values = session.query(Diagnostics).filter(date>=date).filter(date<=endDate).filter_by(model=model).all()
        elif model and ip:
            values = session.query(Diagnostics).filter_by(model=model, addr=ip).all()
        elif ip and date and endDate:
            values = session.query(Diagnostics).filter(date>=date).filter(date<=endDate).filter_by(addr=ip).all()
        elif ip:
            values = session.query(Diagnostics).filter_by(addr=ip).all()
        elif model:
            values = session.query(Diagnostics).filter_by(model=model).all()

        else:
            if date and endDate:
                values = session.query(Diagnostics).filter(date>=date).filter(date<=endDate).all()
            else:
                values = session.query(Diagnostics).all()

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
        endDate = data['endDate']
        if date:
            values = global_session.query(Diagnostics.model, func.count('addr').label('ataques')).filter(Diagnostics.date >= date, Diagnostics.date<=endDate).group_by(Diagnostics.model);
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
