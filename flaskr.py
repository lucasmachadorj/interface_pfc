# coding: utf-8

from flask import Flask, render_template, request, jsonify
import json
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='template')
app.config['DEBUG'] = True
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

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

if __name__ == '__main__':
    app.run()
