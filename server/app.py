#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET', 'POST'])
def campers():

    if request.method == 'GET':
        campers_list = [camper.to_dict(rules=('-signups',)) for camper in Camper.query.all()]
        return campers_list, 200
    
    elif request.method == 'POST':
        try:
            new_camper = Camper(
                name = request.json.get('name'),
                age = request.json.get('age')
            )

            db.session.add(new_camper)
            db.session.commit()
            return new_camper.to_dict(), 201
        except ValueError:
            db.session.rollback()
            return jsonify({'errors': ['validation errors']}), 400
    
@app.route('/campers/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def camper_by_id(id):

    camper = Camper.query.filter(Camper.id == id).first()
    if not camper:
        return {'error': 'Camper not found'}, 404

    elif request.method == "GET":
        return camper.to_dict(), 200
    
    elif request.method == "PATCH":
        try:
            for attr in request.json:
                setattr(camper, attr, request.json.get(attr))
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict(), 202
        except ValueError:
            db.session.rollback()
            return jsonify({'errors': ['validation errors']}), 400
        
@app.route('/activities')
def activities():
    if request.method == 'GET':
        activies_list = [activity.to_dict() for activity in Activity.query.all()]
        return activies_list, 200
    
@app.route('/activities/<int:id>', methods=['GET', 'DELETE'])
def activity_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()
    
    if not activity:
        return {'error': 'Activity not found'}, 404
    if request.method == 'DELETE':
        db.session.delete(activity)
        db.session.commit()
        return {'message': 'Activity successfully deleted'}, 204
    
@app.route('/signups', methods=['GET', 'POST'])
def signups():
    if request.method == 'POST':
        try:
            signup = Signup(
                time = request.json.get('time'),
                camper_id = request.json.get('camper_id'),
                activity_id = request.json.get('activity_id')
            )
            db.session.add(signup)
            db.session.commit()
            return signup.to_dict(), 200
        except ValueError:
            return {'errors': ['validation errors']}, 400
    

if __name__ == '__main__':
    app.run(port=5555, debug=True)
