from flask import Blueprint, request, jsonify
#from flask_login import login_user, logout_user

from src.extensions import db
from src.models import Users, UserSessions, Questions, Options, UserAnswers

import copy

main = Blueprint('main', __name__)

question_reply = {
    "Id": 0,
    "CategoryId": 0,
    "CategoryName": None,
    "QuestionType": 1,
    "Text": "",
    "Options": [],
    "RemainingSecond": 0,
    "Category": None,
    "MasterQuestionId": 0,
    "TotalShowCount": 0,
    "TotalCorrectCount": 0,
    "Percentage": 0
}

options_reply = {
    "Id": 0,
    "QuestionId": 0,
    "Text": "",
    "Point": 0,
    "IsCorrect": None,
    "IsAnswer": None
}

answer = {
    "QuestionId": 0,
    "OptionId":"",
    "AnsweredText": None,
    "ChildQuestionAnsweredText": None,
    "ChildQuestionAnsweredText2": None
}

def create_option_reply(options):

    options_list = []
    for i in range(len(options)):
        o_reply = copy.deepcopy((options_reply))
        o_reply['QuestionId'] = question.id
        o_reply['Id'] = options[i].id
        o_reply['Text'] = options[i].option_text
        o_reply['IsCorrect'] = options[i].option_is_correct
        o_reply['IsAnswer'] = options[i].option_is_answer
        options_list.append(o_reply)

    return options_list

@main.route('/api/v1/assessment/<string:session_id>/question/<int:question_number>', methods=['GET','OPTIONS'])
def get_question(session_id,question_number):

    reply = {}
    code = 200
    if request.method == 'GET':

        if UserSessions.query.filter(UserSessions.session_id == session_id).first():
            question = Questions.query.filter(Questions.id == question_number).first()
            options = Options.query.filter(Options.question_id == question_number).all()

            reply = copy.deepcopy(question_reply)

            reply['CategoryName'] = question.question_category
            reply['Options'] = create_option_reply(options)
            reply['Text'] = question.question_text
        else:
            code = 403
            reply = "The session id doesn't exists"

    return jsonify(
    {
        "Status": 1,
        "Message": "Success",
        "Data": reply
    }),code

@main.route('/api/v1/assessment/<string:session_id>/answer', methods=['POST','OPTIONS'])
def save_answer(session_id):

    if request.method == 'POST':

        user = UserSessions.query.filter(UserSessions.session_id == session_id).first()

        question_id = request.json['QuestionId']
        option_id = request.json['OptionId']

        question = Questions.query.filter(Questions.id == question_id).first()
        option = Options.query.filter(Options.id == option_id).first()

        answer = UserAnswers(
            user_id = user.user_id,
            question_id = question_id,
            option_id = option_id,
            category = question.question_category,
            is_correct = option.option_is_correct,
            score = question.question_score
        )

        db.session.add(answer)
        db.session.commit()

        return jsonify({"Status": 1,"Message": "Success","Data": True}),200

    return jsonify({"Status": 1,"Message": "Success","Data": ""}),200


category_answer = {
    "CategoryName": "Bayesian Probability",
    "QuestionCount": 1,
    "Correct": 0,
    "InCorrect": 1,
    "Empty": 0,
    "CorrectTotalScore": 0,
    "TotalScore": 5
}

result_reply = {
    "Id": 169214,
    "TestType": 1,
    "ClientUserId": None,
    "GKey": "",
    "TakerId": 0,
    "TakerName": "",
    "TakerSurname": "",
    "TakerEmail": "",
    "MobilePhone": "",
    "Region": None,
    "UserConfidenceScore": 0.0,
    "QuestionCount": 0,
    "CorrectTotalScore": 0,
    "AssessmentTotalScore": 0,
    "EmptyAnswers": 0,
    "CorrectAnswers": 0,
    "InCorrectAnswers": 0,
    "TimeTaken": "12 minutes, 11 seconds, 857 milliseconds",
    "StartDate": "2021-09-25T18:40:09.983",
    "EndDate": "2021-09-25T18:52:21.84",
    "CreatedDate": "2021-09-25T18:40:08.623",
    "IpAddress": "200.45.177.213",
    "DegreeText": "Bronze",
    "Categories": [],
    "ChildQuestionCategories": [],
    "RqAssessmentScore": None,
    "AssessmentScore211": None,
    "AssessmentSectionScoreDetail": None,
    "RedirectToNewAssessment": None
}

def create_category_reply(answers):

    category_list = []
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

    for value in category_dict.values():
        category_list.append(value)

    return category_list

@main.route('/api/v1/assessment/<string:session_id>/result', methods=['GET','OPTIONS'])
def get_results(session_id):

    result = {}
    code = 200
    if request.method == 'GET':

        user_session = UserSessions.query.filter(UserSessions.session_id == session_id).first()
        if user_session:

            user = Users.query.filter(Users.id == user_session.user_id).first()

            answers = UserAnswers.query.filter(UserAnswers.user_id == user.id).all()

            result = copy.deepcopy(result_reply)

            #result['Categories'] = category_list
            result['Categories'] = create_category_reply(answers)
            result['GKey'] = session_id
            result['TakerId'] = user.id
            result['TakerName'] = user.name
            result['TakerSurname'] = user.surname
            result['TakerEmail'] = user.email

            #TODO: crear una funcion para totalizar preguntas (no por categorias)
            result['QuestionCount'] = 0
            result['CorrectTotalScore'] = 0
            result['AssessmentTotalScore'] = 0
            result['EmptyAnswers'] = 0
            result['CorrectAnswers'] = 0
            result['InCorrectAnswers'] = 0

            #TODO: evaluar la forma de obtener el tiempo que le lleva al usuario completar el examne
            result['TimeTaken'] = None
            result['StartDate'] = None
            result['EndDate'] = None
            result['CreateDate'] = None

        else:
            code = 403
            result = "The session id doesn't exists"

    return jsonify(
    {
        "Status": 1,
        "Message": "Success",
        "Data": result
    }),code

