# Rest Api for bank management implementation
from flask import Flask, request, jsonify, Response
import pymysql.cursors
import json
from random import randint

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
    # creating cursor
    mycursor = mydb.cursor()
except:
    print("Error creating cursor")


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


# get route to get details of all the transactions
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


# post request to deposit money in your bank account
@app.route('/deposit', methods=["POST"])
def deposit():
    data = request.json
    print(data)
    account_number = data['account_number']
    amount = float(data['amount'])
    query = "SELECT account_number from account_holder where account_number = '{}'".format(account_number)
    try:
        mycursor.execute(query)
        account = mycursor.fetchone()
        if account:
            if amount > 0 and account_number:
                print("account_number", account_number)
                print("amount", amount)
                query = "SELECT balance from account_balance where account_number = '{}'".format(account_number)
                mycursor.execute(query)
                balance = mycursor.fetchone()
                balance = float(balance['balance'])
                final_amount = amount + balance
                query = "UPDATE account_balance SET balance = {} where account_number = '{}'".format(final_amount,
                                                                                                     account_number)
                try:
                    mycursor.execute(query)
                    query = "INSERT INTO account_history(account_number, payment_type, balance_before, balance_afterwards, comments) values" \
                            "({}, 'deposit', {}, {}, 'Deposit made in account')".format(account_number, balance,
                                                                                        final_amount)
                    try:
                        mycursor.execute(query)
                        return jsonify({
                            "message": "Deposit record successfully added",
                            "status_code": "200"
                        })
                    except:
                        print("Error")
                except:
                    print("Error")
                return jsonify({
                    "message": "money deposited",
                    "status_code": 200
                })
            else:
                return jsonify({
                    "error": "Please send account number and amount both amount should be greater than zero",
                    "status_code": 200
                })
        else:
            return jsonify({
                "status_code": 200,
                "error": "account number incorrect"
            })
    except:
        return jsonify({
            "error": "error fetching records",
            "status_code": 200
        })


# post request to withdraw money from your bank account
@app.route("/withdrawal", methods=['POST'])
def withdrawal():
    data = request.json
    account_number = data['account_number']
    amount = data['amount']
    query = "SELECT account_number from account_holder where account_number = '{}'".format(account_number)
    try:
        mycursor.execute(query)
        account = mycursor.fetchone()
        if account:
            if amount > 0 and account_number:
                try:
                    query = "SELECT balance FROM account_balance WHERE account_number = '{}'".format(account_number)
                    mycursor.execute(query)
                except:
                    balance = float(mycursor.fetchone()['balance'])
                if balance >= amount:
                    balance_after_withdrawal = balance - amount
                    try:
                        query = "UPDATE account_balance SET balance = {} WHERE account_number = '{}'".format(
                            balance_after_withdrawal,
                            account_number)
                        mydb.commit()
                        mycursor.execute(query)
                        query = "INSERT INTO account_history(account_number, payment_type, balance_before, balance_afterwards, comments) values" \
                                "({}, 'withdraw', {}, {}, 'Withdrawal made from the account')".format(account_number,
                                                                                                      balance,
                                                                                                      balance_after_withdrawal)
                        try:
                            mycursor.execute(query)
                            mydb.commit()
                            return jsonify({
                                "message": "ammount_successfully_debited",
                                "status_code": 200,
                                "balance_after_withdrawal": balance_after_withdrawal
                            })
                        except:
                            return jsonify({
                                "message": "error contact customer care",
                                "status_code": 200
                            })
                    except:
                        print("Error in updating balance")
                else:
                    print("Insufficient funds in your bank account")
                    return jsonify({
                        "error": "insufficient funds",
                        "status_code": 200
                    })
            else:
                print("Error")
                return jsonify({
                    "error": "amount should be greater than zero",
                    "status_code": "200"
                })
        else:
            print("account number invalid")
            return jsonify({
                "error": "invalid account number please try again with correct one",
                "status_code": 200
            })

    except:
        print("Error in retreiving account number")
        return jsonify({
            "message": "error",
            "status": 200
        })


# post request to create account
@app.route("/createuser", methods=['POST'])
def create_user():
    data = request.json
    print(data)
    account_holder_name = data['account_holder']
    email = data['email']
    address = data['address']
    phone_number = data['phone_number']
    account_type = data['account_type']
    amount = data['amount']
    account_number = str(randint(100 ** 9, (100 ** 10) - 1))
    if len(account_holder_name) > 0 and len(address) > 2 and len(phone_number) > 0 and len(account_type) > 0 and len(
            email) > 3 and float(amount) > 0:
        try:
            query = "INSERT INTO account_holder(account_holder, email, address, phone_number, account_number, account_type, amount) VALUES" \
                    "('{}','{}','{}','{}','{}','{}',{})".format(account_holder_name, email, address, phone_number,
                                                                account_number, account_type, float(amount))
            print(query)
            mycursor.execute(query)
            try:
                query = "INSERT INTO account_balance(account_number, balance) VALUES " \
                        "('{}', {})".format(account_number, amount)
                mycursor.execute(query)
                try:
                    query = "INSERT INTO account_history(account_number, payment_type, balance_before, balance_afterwards, comments) values " \
                            "('{}', 'deposit', 0, {}, 'Deposit made on account opening')".format(account_number, amount)
                    mycursor.execute(query)
                    print("Your Account has been successfully created")
                    return jsonify({
                        "message": "Your Account is successfully created",
                        "account_number": account_number,
                        "status_code": 200,
                        "message": "Keep this Account Number safe as it is very important and will be used for further transactions"
                    })

                except:
                    return jsonify({
                        "error": "Error updating deposit for your account in the ledger",
                        "status_code": 200
                    })
            except:
                return jsonify({
                    "error": "Error updating balance in your new account",
                    "status_code": 200
                })

        except:
            return jsonify({
                "error": "There was some error in creating you account please try again later",
                "status_code": 200
            })
    else:
        return jsonify({
            "error": "",
            "status_code": 200
        })


# post request to transfer money from one account to other account
@app.route("/transfer", methods=['POST'])
def transfer():
    data = request.json
    account_number = data['account_number']
    amount = data['amount']
    your_account_number = data['your_account_number']
    mycursor.execute(
        "SELECT account_number FROM account_holder WHERE account_number = '{}'".format(your_account_number))
    account_number_ = mycursor.fetchone()
    if account_number_:
        print("Valid account number")
    else:
        return jsonify({
            "error": "your_account_number_invalid",
            "status_code": 200
        })
    mycursor.execute(
        "SELECT account_number FROM account_holder WHERE account_number = '{}'".format(account_number))
    account_number_ = mycursor.fetchone()
    if account_number_:
        print("Valid account number")
    else:
        return jsonify({
            "error": "account_number_invalid",
            "status_code": 200
        })
    if amount <= 0:
        return jsonify({
            "error": "transaction amount is equal to zero or less tham zero",
            "status_code": 200
        })
    try:
        query = "SELECT balance FROM account_balance WHERE account_number = '{}'".format(your_account_number)
        mycursor.execute(query)
        balance = mycursor.fetchone()['balance']
        balance = float(balance)
        if balance >= amount:
            balance_new = balance - amount
            try:
                query = "UPDATE account_balance SET balance = {} WHERE account_number = '{}'".format(balance_new,
                                                                                                     your_account_number)
                mycursor.execute(query)
                mydb.commit()
            except:
                return jsonify({
                    "error": "error updating balance",
                    "status_code": 200
                })
            try:
                query = "UPDATE account_balance SET balance = balance + {} WHERE account_number = '{}'".format(
                    amount,
                    account_number)
                mycursor.execute(query)
                mydb.commit()
            except:
                return jsonify({
                    "error": "error updating balance",
                    "status_code": 200
                })
            new_balance = 0
            try:
                query = "SELECT balance FROM account_balance WHERE account_number = '{}'".format(account_number)
                mycursor.execute(query)
                new_balance = float(mycursor.fetchone()['balance'])
            except:
                return jsonify({
                    "error": "error selecting balance",
                    "status_code": 200
                })
            try:
                query = "INSERT INTO account_history(account_number, payment_type, balance_before, balance_afterwards, comments) values" \
                        "({}, 'withdraw', {}, {}, 'Money transferred {} to account_number {}')".format(
                    your_account_number,
                    balance,
                    balance_new,
                    amount,
                    account_number)
                mycursor.execute(query)
                mydb.commit()
            except:
                return jsonify({
                    "error": "error creating transaction",
                    "status_code": 200
                })
            try:
                query = "INSERT INTO account_history(account_number, payment_type, balance_before, balance_afterwards, comments) values" \
                        "({}, 'deposit', {}, {}, 'Money recieived {} from  account_number {}')".format(
                    your_account_number,
                    new_balance - amount,
                    new_balance,
                    amount,
                    account_number)
                mycursor.execute(query)
                mydb.commit()
            except:
                return jsonify({
                    "error": "error updating balance",
                    "status_code": 200
                })
            return jsonify({
                "message": "transaction successfull",
                "comments": "money successfully transfered",
                "status_code": 200
            })
        else:
            return jsonify({
                "error": "insufficient funds in your account please try again later",
                "status_code": 200
            })
    except:
        print("Error in getting balance")


if __name__ == '__main__':
    app.run()
