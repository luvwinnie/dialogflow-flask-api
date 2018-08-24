# -*- coding: utf-8 -*-
from __future__ import print_function
from flask import Flask, request, jsonify
from flask_assistant import Assistant, ask, tell, context_manager
import requests
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

app = Flask(__name__)
assist = Assistant(app, route='/')


@assist.action('give-employee')
def retrieve_position():
    if request.headers['Content-Type'] != "application/json; charset=UTF-8":
        print(request.headers['Content-Type'])
        return jsonify(res='error'), 400

    name = request.json["result"]["parameters"]["employee"]
    familyName = name[0:2]
    givenName = name[2:]

    # ここにAPIを呼ぶ処理
    baseUrl = "http://leow.tk"

    apiUrl = baseUrl + "/" + familyName + "/" + givenName + "/" + "position"
    result = requests.get(apiUrl)
    if result.status_code != 200:
        return jsonify(res='error'), 400

    json = result.json()
    position = json[0]["position"]
    speech = familyName + "さんは" + position + "にいます。"
    print(speech)
    return ask(speech)

@assist.action('get-place-employees')
def retrieve_employees():
    if request.headers['Content-Type'] != "application/json; charset=UTF-8":
        print(request.headers['Content-Type'])
        return jsonify(res='error'), 400

    position = request.json["result"]["parameters"]["position"]

    baseUrl = "http://leow.tk"
    apiUrl = baseUrl + "/" + position + "/employees"
    result = requests.get(apiUrl)
    if result.status_code != 200:
        speech = position + "はどこなのかがわかりません"
        return ask(speech)

    speech = "エントランスには"
    employees = result.json()
    for employee in employees:
        speech += employee["family_name"] + ","
    number_of_employees = str(len(employees))
    
    speech += "がいます。"
    context_manager.add('number-of-employees',lifespan=1)
    context_manager.set('number-of-employees', 'num', number_of_employees)
    context_manager.set('number-of-employees', 'employees', employees)
    return ask(speech)

@assist.action('get-employees-places')
def retrieve_employees_places():
    if request.headers['Content-Type'] != "application/json; charset=UTF-8":
        print(request.headers['Content-Type'])
        return jsonify(res='error'), 400

    baseUrl = "http://leow.tk"
    apiUrl = baseUrl + "/" + "employees_position"
    result = requests.get(apiUrl)
    if result.status_code != 200:
        speech = "職員が一人も見つかりませんでした"
        return ask(speech)

    employees = result.json()
    logging.debug("{}".format(employees))
    places = dict()
    for employee in employees:
        if employee["position"] not in places:
            places[employee["position"]] = [employee["family_name"]]
            continue
        places[employee["position"]].append(employee["family_name"])
    # print(places.keys())
    speech = ""
    for place, all_employees in places.items():
        speech += place + "にいるのは"
        logging.debug(place, all_employees)
        for employee in all_employees:
            speech += "," + employee + "さん"
        speech += ". "
    speech += "です"

    return ask(speech)

@assist.action('get-weekly-study-time')
def get_study_time():
    if request.headers['Content-Type'] != "application/json; charset=UTF-8":
        print(request.headers['Content-Type'])
        return jsonify(res='error'), 400
    scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('asiaquest-intern-leow-3e0b0d31061a.json', scope)
    gc = gspread.authorize(credentials)
    worksheet = gc.open('weekly_report').sheet1
    total_study_time = worksheet.acell('E19')
    
    if total_study_time != "":
        speech += "グーグルスプレッドシートに合計勉強時間が記入されていません"
    
    speech = "合計勉強時間は" + total_study_time.value
    return ask(speech)


@assist.context('number-of-employees')
@assist.action('get-number-employees')
def retrieve_employees_number():
    if request.headers['Content-Type'] != "application/json; charset=UTF-8":
        print(request.headers['Content-Type'])
        return jsonify(res='error'), 400

    num_employees = request.json["result"]["contexts"][0]["parameters"]["num"]
    speech = num_employees + "人です。"
    logging.debug("number of {}".format(speech))
    return ask(speech)
    





if __name__ == '__main__':
    app.run()
