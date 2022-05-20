import traceback

import pymongo as pymongo
from flask import Flask, request, jsonify, session
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask_session import Session


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["user_profile"]
user = mydb["user_details"]
unique_id = mydb["unique_id"]
task_list = mydb["task_list"]

app = Flask(__name__)
app.config['SECRET_KEY'] = "it's my secretkey, don't expose it"
app.config["SESSION_PERMANENT"] = True  # enabling session expiry
app.permanent_session_lifetime = timedelta(minutes=5)  # 5 minutes expiry
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
bcrypt = Bcrypt(app)
import email_to

server = email_to.EmailServer('smtp.gmail.com', 587, 'waseemakramaz98@gmail.com', 'Was786eem!@98')
message = server.message()
import random


@app.route('/user/login', methods=['POST'])
def user_login():
    user_name = request.json.get('user_name')
    password = request.json.get('password')

    login_user = user.find_one({'user_name': user_name})

    if login_user:
        pw_hash = bcrypt.generate_password_hash(password)
        cross_check = bcrypt.check_password_hash(pw_hash, password)
        if cross_check == True:
            session['user_name'] = user_name
            # print(session['user_name'])
            for id in mydb["user_details"].find({"user_name": user_name}, {"_id": 0}):
                return jsonify({"message": "login successful!","user_id": id["user_id"]})
    return jsonify({"message": "invalid user_name/password"})



@app.route('/register', methods=['POST', 'GET'])
def register():
    global existing_user, password, user_exist, user_name, user_email, user_designation, user_department, user_DOB, user_img, user_phone_no
    if request.method == 'POST':
        user_name = request.json.get('user_name')
        password = request.json.get('password')
        user_email = request.json.get('user_email')
        user_designation = request.json.get('user_designation')
        user_department = request.json.get('user_department')
        user_DOB = request.json.get('user_DOB')
        user_img = request.json.get('user_img')
        user_phone_no = request.json.get('user_phone_no')
        user_exist = user.find_one({'user_name': user_name})

    if user_exist is None:
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        user.insert_one({'user_name': user_name, "password": pw_hash, "user_email": user_email,
                         "user_designation": user_designation, "user_department": user_department,
                         "user_DOB": user_DOB,"user_img":user_img,"user_phone_no":user_phone_no})
        for latest_usr_id in mydb["unique_id"].find({"key": "user"}, {"_id": 0, "user_id": 1}):
            mydb["user_details"].update_one({'user_name': user_name},
                                            {'$set': {"user_id": int(latest_usr_id['user_id']) + 1}})

            mydb["unique_id"].update_one({'key': 'user'}, {'$set': {"user_id": int(latest_usr_id['user_id']) + 1}})
        session['user_name'] = user_name
        # print(session['user_name'])
        for i in user.find({"user_name": user_name}, {"_id": 0}):
            return jsonify({"message": "successfully registered", "user_id": i["user_id"]})
    return jsonify({"message": "user_already exist"})


@app.route("/forget_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        user_email = request.json.get('user_email')
        s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        passlen = 16
        generated_password = "".join(random.sample(s, passlen))
        user.update_one({'user_email': user_email},
                        {'$set': {"password": generated_password}})  #######updating mailed password
        server = email_to.EmailServer('smtp.gmail.com', 587, 'waseemakramaz98@gmail.com',
                                      'Was786eem!@98')
        message = server.message()
        message.add(generated_password)
        message.send(user_email, 'Password attchment')
        return jsonify({"message": "message sent!"})


# @app.route("/get_body", methods=['GET', 'POST'])
# def get_body():
#     # my_user_details
#     user_name = request.json.get('user_id')
#     # user_exist = user.find_one({'user_name': user_name})
#     logged_user = [doc for doc in mydb.user_details.find({'user_name': user_name}, {'_id': 0})]
#     user_body = mydb.user_details.find({'user_name': user_name}, {'_id': 0})
#     return jsonify({"logged_user": logged_user})

@app.route("/update_todolist", methods=['GET', 'POST'])
def update_todolists():
    user_id = request.json.get('user_id')
    user_todo = request.json.get('user_todo')
    user_date = request.json.get('user_date')
    user_up = "false"
    task_list.insert_one({'user_id': user_id, "user_todo": user_todo, "user_date": user_date,"user_up":user_up})
    return jsonify({"message": "successfully inserted"})


@app.route("/get_todolist", methods=['GET', 'POST'])
def get_todolists():
    user_id = request.json.get("user_id")
    # logged_user = [doc for doc in mydb.user_details.find({'user_name': user_name}, {'_id': 0})]
    task_lists = [t for t in
                  task_list.find({"user_id": user_id}, {'_id': 0})]  # returning complete lists task as per user_ id
    return jsonify({"list": task_lists})


# @app.route("/user_lists", methods=['GET', 'POST'])
# def user_lists():
#     # user = []
#     # a =  mydb.user_details.find()
#     all_user = [doc for doc in mydb.user_details.find({}, {'_id': 0})]
#     # for user in mydb.user_details.find({},{'_id':0}):
#     return jsonify({'user': all_user})
#

# @app.route("/user_details", methods=['GET', 'POST'])
# def user_details():
#     user_id = request.json.get('user_id')
#     task = request.json.get('task_list')
#     import datetime
#
#     date_object = "18/05/2022"
#     # today = date.today()
#     # print("Today's date:", today)
#     exist = task_list.find({"user_id": user_id})
#     if exist is None:
#         cur_task = task_list.insert_one({"user_id": user_id, "today": date_object, "task_list": task})
#         return jsonify({"message": "data inserted successfully"})
#     return jsonify({'message': "user exist", "cur_task": cur_task})

# curr_task = [doc for doc in task_list.find({}, {'_id': 0})]

# curr_task =task_list.find({"user_id": user_id})
# return jsonify({'curr_task': curr_task})
@app.route("/user_profile", methods=['GET', 'POST'])
def user_profile():
    user_id = request.json.get("user_id")
    for users in mydb["user_details"].find({"user_id":user_id},{'_id':0,"password":0}):
        return jsonify({"users":users})


# @app.route("/save_todolist", methods=['GET', 'POST'])
# def save_todolist():
#     stack_list = request.json.get()
@app.route("/get_users", methods=['GET', 'POST'])
def get_users():
        logged_user = [doc for doc in mydb.user_details.find({}, {'_id': 0,"password": 0})]
        return jsonify({"users": logged_user})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
