from flask import Blueprint, request, jsonify
#from flask_login import login_user, logout_user

from src.extensions import db
from src.models import Users, UserSessions, Questions, Options, UserAnswers

from src.templates import question_reply, options_reply, answer, category_answer, result_reply

import copy

main = Blueprint('main', __name__)


def create_option_reply(question_id,options):

    options_list = []
    for i in range(len(options)):
        o_reply = copy.deepcopy((options_reply))
        o_reply['QuestionId'] = question_id
        o_reply['Id'] = options[i].id
        o_reply['Text'] = options[i].option_text
        o_reply['IsCorrect'] = options[i].option_is_correct
        o_reply['IsAnswer'] = options[i].option_is_answer
        options_list.append(o_reply)

    return options_list

@main.route('/api/v1/assessment/<string:session_id>/question/<int:question_number>', methods=['GET','OPTIONS'])
def get_question(session_id,question_number):

    if request.method == 'GET':

        code = 404
        reply = "The session id doesn't exists"
        if UserSessions.query.filter(UserSessions.session_id == session_id).first():
            code = 200
            question = Questions.query.filter(Questions.id == question_number).first()
            options = Options.query.filter(Options.question_id == question_number).all()

            reply = copy.deepcopy(question_reply)

            reply['CategoryName'] = question.question_category
            reply['Options'] = create_option_reply(question.id,options)
            reply['Text'] = question.question_text

        return jsonify(
        {
            "Status": 1,
            "Message": "Success",
            "Data": reply
        }),code

    return "",200

@main.route('/api/v1/assessment/<string:session_id>/answer', methods=['POST','OPTIONS'])
def save_answer(session_id):

    if request.method == 'POST':

        user_session = UserSessions.query.filter(UserSessions.session_id == session_id).first()

        code = 404
        reply = "The session id doesn't exists"
        if user_session:

            code = 200
            reply = True

            question_id = request.json['QuestionId']
            option_id = request.json['OptionId']

            question = Questions.query.filter(Questions.id == question_id).first()
            option = Options.query.filter(Options.id == option_id).first()

            answer = UserAnswers(
                user_id = user_session.user_id,
                question_id = question_id,
                option_id = option_id,
                category = question.question_category,
                is_correct = option.option_is_correct,
                score = question.question_score
            )

            #TODO: add try/execpt in case db connection is down
            db.session.add(answer)
            db.session.commit()

        return jsonify({"Status": 1,"Message": "Success","Data": reply}),code

    return "",200



def create_category_reply(answers):

    category_dict = {}
    for i in range(len(answers)):
        if answers[i].category not in category_dict.keys():
            category_dict[answers[i].category] = {
                "CategoryName": answers[i].category,
                "QuestionCount": 0,
                "Correct": 0,
                "InCorrect": 0,
                "Empty": 0,
                "CorrectTotalScore": 0,
                "TotalScore": 0
            }
        category_dict[answers[i].category]['QuestionCount']+=1
        if answers[i].is_correct:
            category_dict[answers[i].category]['Correct']+=1
            category_dict[answers[i].category]['CorrectTotalScore']+=answers[i].score
        else:
            category_dict[answers[i].category]['InCorrect']+=1
        category_dict[answers[i].category]['TotalScore']+=answers[i].score

    return [value for value in category_dict.values()]

def question_totalizer(answers, result):

    for i in range(len(answers)):
        result['QuestionCount']+=1
        if answers[i].is_correct:
            result['CorrectAnswers']+=1
            result['CorrectTotalScore']+=answers[i].score
        else:
            result['InCorrectAnswers']+=1
        result['AssessmentTotalScore']+=answers[i].score

from datetime import datetime, timedelta

def question_time_taken(user_session, result):

    import time
    start_timestamp = user_session.session_init_timestamp
    current_timestamp = time.time()

    #TODO: find another way to parse the taken time in seconds
    time_taken = current_timestamp - start_timestamp #in seconds

    time = str(timedelta(time_taken)).split(':')
    time_taken_min = str(time[1])
    time_taken_sec = str(time[2].split('.')[0])
    time_take_milisec = str(time[2].split('.')[1])

    result['TimeTaken'] = time_taken_min + ' minutes, ' + time_taken_sec + ' seconds, ' + time_take_milisec + ' miliseconds'
    result['StartDate'] = datetime.utcfromtimestamp(start_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    result['EndDate'] = datetime.utcfromtimestamp(current_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    result['CreateDate'] = datetime.utcfromtimestamp(start_timestamp).strftime('%Y-%m-%d %H:%M:%S')

@main.route('/api/v1/assessment/<string:session_id>/result', methods=['GET','OPTIONS'])
def get_results(session_id):

    if request.method == 'GET':

        code = 404
        result = "The session id doesn't exists"

        user_session = UserSessions.query.filter(UserSessions.session_id == session_id).first()
        if user_session:

            code = 200
            result = copy.deepcopy(result_reply)

            user = Users.query.filter(Users.id == user_session.user_id).first()
            answers = UserAnswers.query.filter(UserAnswers.user_id == user.id).all()

            result['Categories'] = create_category_reply(answers)
            result['GKey'] = session_id
            result['TakerId'] = user.id
            result['TakerName'] = user.name
            result['TakerSurname'] = user.surname
            result['TakerEmail'] = user.email

            question_totalizer(answers, result)

            question_time_taken(user_session, result)

        return jsonify(
        {
            "Status": 1,
            "Message": "Success",
            "Data": result
        }),code

    return "", 200

