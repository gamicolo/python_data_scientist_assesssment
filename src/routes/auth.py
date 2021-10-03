from flask import Blueprint, request, jsonify
#from flask_login import login_user, logout_user

from src.extensions import db
from src.models import Users, UserSessions

import uuid
import copy

from src.templates import test_reply

auth = Blueprint('auth', __name__)

@auth.route('/api/v1/assessment/create/<int:parent_id>', methods=['POST','OPTIONS'])
def register(parent_id):

    if request.method == 'POST':
        name = request.json['Name']
        surname = request.json['Surname']
        email = request.json['Email']
        session_id = str(uuid.uuid4())

        user = Users(
            name = name, 
            surname = surname, 
            email = email
        )

        if not(Users.query.filter(Users.email == email)):
            #TODO: add a try/except in case the DB is down
            db.session.add(user)
            db.session.commit()

            user_session = UserSessions(
                user_id = user.id,
                session_id = session_id
            )

            #TODO: add a try/except in case the DB is down
            db.session.add(user_session)
            db.session.commit()
        else:
            user = Users.query.filter(Users.email == email).first()
            session_id = UserSessions.query.filter(UserSessions.user_id == user.id).first().session_id

        return jsonify({"Status": 1,"Message": "Success","Data": session_id}),200

    return "",200

@auth.route('/api/v1/assessment/<string:session_id>/test', methods=['GET','OPTIONS'])
def save_timestamp(session_id):

    if request.method == 'GET':
        ts = request.args.get('tsp')
        reply = True
        code = 200

        user_session = UserSessions.query.filter(UserSessions.session_id == session_id).first()
        code = 404
        reply = "The session id doesn't exists"

        if (user_session):
            code = 200
            user = Users.query.filter(Users.id == user_session.user_id).first()
            reply = copy.deepcopy(test_reply)
            reply['Taker']['Id'] = user.id
            reply['Taker']['Email'] = user.email
            reply['Taker']['Name'] = user.name
            reply['Taker']['Surname'] = user.surname

        return jsonify(
        {
            "Status": 1,
            "Message": "Ok",
            "Data": reply
        }),code

    return "",200

@auth.route('/api/v1/assessment/<string:session_id>/start', methods=['POST','OPTIONS'])
def start_test(session_id):

    #TODO: save here the TS from the previous request?

    if request.method == 'POST':
        reply = True
        code = 200
        if not(UserSessions.query.filter(UserSessions.session_id == session_id).first()):
            code = 404
            reply = "The session id doesn't exists"
            
        return jsonify(
        {
            "Status": 1,
            "Message": "Success",
            "Data": reply
        }),code

    return "",200
