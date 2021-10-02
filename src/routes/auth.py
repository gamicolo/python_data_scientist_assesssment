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

        db.session.add(user)
        db.session.commit()

        user_session = UserSessions(
            user_id = user.id,
            session_id = session_id
        )

        db.session.add(user_session)
        db.session.commit()

        return jsonify({"Status": 1,"Message": "Success","Data": session_id}),200

    return jsonify({"Status": 1,"Message": "Success","Data": ""}),200
