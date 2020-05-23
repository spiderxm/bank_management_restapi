from flask import Flask, request, jsonify, Response
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
                        "status_code": 200})


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
                            "status_code": 200})
    except:
        return jsonify({"status": 'failure',
                        "reason": 'error querying table',
                        "status_code": 200})


# get route to show all transaction details of a particular account
@app.route('/passbook/<account_number>')
def passbook(account_number):
    mycursor.execute("SELECT account_number FROM account_holder where account_number = '{}'".format(account_number))
    account = mycursor.fetchall()
    if account:
        print(account_number)
        try:
            query = "SELECT * FROM account_history WHERE account_number = '{}'".format(account_number)
            mycursor.execute(query)
            records = []
            record = mycursor.fetchone()
            while record:
                r = {
                    "Transaction type :": record['payment_type'],
                    "Balance before transaction : ": float(record['balance_before']),
                    "Balance after transaction :": float(record['balance_afterwards']),
                    "Date and time of transaction :": record['transaction_time'],
                    "Message ": record['comments']
                }
                records.append(r)
                record = mycursor.fetchone()
            return jsonify(records)
        except:
            return jsonify({
                "status_code": 200,
                "status": "failure",
                "error": "error finding history"
            })

    else:
        return Response(json.dumps({"status": "failure account number does not exist", "status_code": "200"}),
                        mimetype="application/json",
                        status=200)


@app.route("/transactiondetails")
def details():
    try:
        query = "SELECT * FROM account_history ORDER BY transaction_time ASC"
        mycursor.execute(query)
        records = []
        record = mycursor.fetchone()
        transactionnumber: int = 1
        while record:
            r = {
                "Transaction number": transactionnumber,
                "Transaction type :": record['payment_type'],
                "Balance before transaction : ": float(record['balance_before']),
                "Balance after transaction :": float(record['balance_afterwards']),
                "Date and time of transaction :": record['transaction_time'],
                "Message ": record['comments']
            }
            records.append(r)
            record = mycursor.fetchone()
            transactionnumber = transactionnumber + 1
        return jsonify(records)
    except:
        return jsonify({
            "status_code": 200,
            "status": "failure",
            "error": "error finding history of transactions"
        })


@app.route("/deposit/<account_number>", methods=['POST'])
def deposit(account_number):
    print("deposit money")


@app.route("/withdrawal/<account_number>", methods=['POST'])
def withdrawal(account_number):
    print("withdraw amount")


# get route to get total number of account holder and type of account holder
@app.route("/account-type-details")
def account_type_details():
    query = "SELECT COUNT(*) AS users FROM account_holder"
    try:
        mycursor.execute(query)
        users = mycursor.fetchone()
        users = users['users']
        details = []
        details.append({
            "total_number_of_users": users
        })
        query1 = "SELECT COUNT(*) AS users FROM account_holder where account_type = 'lite'"
        query2 = "SELECT COUNT(*) AS users FROM account_holder where account_type = 'elite'"
        query3 = "SELECT COUNT(*) AS users FROM account_holder where account_type = 'executive'"
        try:
            mycursor.execute(query1)
            users = mycursor.fetchone()
            users = users['users']
            details.append({
                "total_number_of_lite_users": users
            })
            mycursor.execute(query2)
            users = mycursor.fetchone()
            users = users['users']
            details.append({
                "total_number_of_elite_users": users
            })
            mycursor.execute(query3)
            users = mycursor.fetchone()
            users = users['users']
            details.append({
                "total_number_of_executive_users": users
            })
            return jsonify(details)
        except:
            return jsonify({"Status": "failure", "status_code": 200})

    except:
        print("error")
        return jsonify({"Status": "failure", "status_code": 200})


# get route to show details related to money in the bank
@app.route('/money-details')
def money_details():
    query = "SELECT SUM(balance) as total_money FROM account_balance"
    query1 = "SELECT Count(*) as total_users FROM account_balance"
    query2 = "SELECT balance as min_balance FROM account_balance ORDER BY balance limit 1"
    query3 = "SELECT balance as max_balance FROM account_balance ORDER BY balance DESC limit 1"
    try:
        mycursor.execute(query)
        amount = mycursor.fetchone()
        amount = float(amount['total_money'])
        mycursor.execute(query1)
        users = mycursor.fetchone()
        users = users['total_users']
        mycursor.execute(query2)
        minimum = float(mycursor.fetchone()['min_balance'])
        mycursor.execute(query3)
        maximum = float(mycursor.fetchone()['max_balance'])
        return jsonify({
            "average money per bank account": amount,
            "total money in bank": amount / users,
            "minimum money in a account": minimum,
            "maximum money in a bank account": maximum

        })
    except:
        return jsonify({
            "status_code": 200,
            "error": "error getting transaction details"
        })


if __name__ == '__main__':
    app.run()
