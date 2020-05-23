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
        return {"status_code": 400}


# @app.route('/create_user', methods=['POST'])
# def create_user:


if __name__ == '__main__':
    app.run()
