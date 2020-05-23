from flask import Flask, request, jsonify
import pymysql.cursors
import json

app = Flask(__name__)

mydb = pymysql.connect(
    host='bank.ct1ikgzgdh96.us-east-1.rds.amazonaws.com',
    user='admin',
    password='adminadmin',
    db='BANK',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

try:
    mycursor = mydb.cursor()
except:
    print("Error")


# get route to get details of all the account holders
@app.route('/users')
def hello_world():
    query = "SELECT * FROM account_holder"
    try:
        mycursor.execute(query)
        # print(mycursor.fetchall())
        a = mycursor.fetchone()
        print(a)
        records = []
        while a:
            record = {
                "account_holder": a['account_holder'],
                "email": a['email'],
                "address": a['address'],
                "phone_number": a['phone_number'],
                "account_number": a['account_number'],
                "account_type": a['account_type'],
                "creation_time": a['account_creation_time']
            }
            records.append(record)
            a = mycursor.fetchone()
        # print(records)
        return jsonify(records)
    except:
        print("Error")
        return jsonify({"status": 'failure',
                        "reason": 'error fetching records',
                        "status_code": 400})


# get route to get the balance of a particular account number
@app.route("/balance/<account_number>")
def get_balance(account_number):
    query = "Select balance from account_balance where account_number = '{}'".format(account_number)
    try:
        mycursor.execute(query)
        a = mycursor.fetchone()
        print(a)
        if a:
            result = {
                "account_number": account_number,
                "current_balance": float(a['balance']),
                "status_code": 200
            }
            return jsonify(result)
        else:
            return jsonify({"status": 'failure',
                            "reason": 'error account number does not exist',
                            "status_code": 400})
    except:
        return jsonify({"status": 'failure',
                        "reason": 'error querying table',
                        "status_code": 400})




if __name__ == '__main__':
    app.run()
