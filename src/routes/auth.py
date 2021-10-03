from flask import Blueprint, request, jsonify
#from flask_login import login_user, logout_user

from src.extensions import db
from src.models import Users, UserSessions

import uuid

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

        return jsonify({"Status": 1,"Message": "Success","Data": session_id}),200

    return jsonify({"Status": 1,"Message": "Success","Data": ""}),200

@auth.route('/api/v1/assessment/<string:session_id>/test', methods=['GET','OPTIONS'])
def save_timestamp(session_id):

    print(request)

    print(request.args.get('tsp'))

    if request.method == 'GET':
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

@auth.route('/api/v1/assessment/<string:session_id>/start', methods=['POST','OPTIONS'])
def start_test(session_id):

    #TODO: save the TS from the previous request?

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
