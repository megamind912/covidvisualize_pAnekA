from db import Database
from geocode import geocode, lonlat_distance
from polylines import find_line
from flask import Flask, request, redirect, url_for
from os.path import join as path_to
from jinja2 import Template
import sqlite3
import requests
import random
import hashlib
from math import ceil
from urllib.parse import quote
import json

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login')
def login():
    if request.method == 'GET':
        with open(path_to(r'static\auth', 'auth.html'), 'r', encoding='utf-8') as file:
            styles = path_to(r'static\css', 'styles.css')
            with open(styles, 'r', encoding='utf-8') as styles:
                return Template(file.read()).render({'styles': styles.read()})
    elif request.method == 'POST':
        db = Database('user.db')
        print(request.form['mail'])
        passw = hashlib.sha224(bytes(request.form['passw1'], encoding='utf-8'))
        passw = passw.hexdigest()
        print(passw)
        res = db.get_info(request.form['mail'], 'password', 'auth')
        print(res)
        if res[1] == 200:
            if passw == res[0][0][0]:
                res = redirect(url_for('profile'))
                res.set_cookie('email', request.form['mail'], max_age=60 * 60 * 24 * 365 * 2)
                return res
            else:
                return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        with open(path_to(r'static\auth', 'reg.html'), 'r', encoding='utf-8') as file:
            styles = path_to(r'static\css', 'styles.css')
            with open(styles, 'r', encoding='utf-8') as styles:
                return Template(file.read()).render({'styles': styles.read()})
    elif request.method == 'POST':
        db = Database('user.db')
        # print(request.form['login'])
        # print(request.form['mail'])
        # print(request.form['passw1'])
        # print(request.form['passw2'])
        if request.form['passw1'] == request.form['passw2']:
            passw = hashlib.sha224(bytes(request.form['passw1'], encoding='utf-8'))
            passw = passw.hexdigest()
            print(passw)
            res = db.add_user(request.form['mail'], passw)
            if res[1] == 200:
                res = redirect(url_for('profile'))
                res.set_cookie('email', request.form['mail'], max_age=60 * 60 * 24 * 365 * 2)
                return res
            else:
                return redirect(url_for('register'))
        else:
            return redirect(url_for('register'))


@app.route('/profile', methods=['GET'])
def profile():
    db = Database('user.db')
    name = request.cookies.get('email')
    res = db.get_info(name, 'home_geopos, work_geopos, school_geopos', 'profile')
    place1, place2, place3 = res[0][0]
    print(name)
    with open(path_to(r'static\auth', 'profile.html'), 'r', encoding='utf-8') as file:
        styles = path_to(r'static\css', 'styles1.css')
        with open(styles, 'r', encoding='utf-8') as styles:
            print(db.get_info(name, 'status', 'profile'))
            try:
                idd = db.get_info(name, 'id', 'auth')
                print(idd, '567483920')
                return Template(file.read()).render({'styles': styles.read(), 'name': name,
                                                     'status': db.get_info(name, 'status', 'profile')[0][0][0],
                                                     'place1': place1, 'place2': place2, 'place3': place3,
                                                     'src': path_to(r'static\images\symptomatics', 'covid.jpg')})
            except IndexError as e:
                print(e, '!!!!!')
                print(file.read(), styles)
                return Template(file.read()).render({'styles': styles.read(), 'name': name,
                                                     'status': 'Ваш статус не установлен'})


@app.route('/reduction', methods=['GET', 'POST'])
def reduction():
    db = Database('user.db')
    if request.method == 'GET':
        name = request.cookies.get('email')
        with open(path_to(r'static\auth', 'reduction.html'), 'r', encoding='utf-8') as file:
            styles = path_to(r'static\css', 'styles1.css')
            with open(styles, 'r', encoding='utf-8') as styles:
                res = Template(file.read()).render(
                    {'styles': styles.read(), 'login': name})
                return res
    elif request.method == 'POST':
        name = request.cookies.get('email')
        status = request.form['status']
        place1 = request.form['place1']
        place2 = request.form['place2']
        place3 = request.form['place3']
        db.put_info('email', name, 'status', status, 'profile')
        print(place1, 111111)
        if place1:
            db.put_info('email', name, 'home_geopos', place1, 'profile')
        if place2:
            db.put_info('email', name, 'place2', place2, 'profile')
        if place3:
            db.put_info('email', name, 'place3', place3, 'profile')
        res = redirect(url_for('profile'))
        return res


@app.route('/map', methods=['GET', 'POST'])
def mapp():
    if request.method == 'GET':
        with open(path_to(r'static\auth', 'map.html'), 'r', encoding='utf-8') as file:
            styles = path_to(r'static\css', 'styles1.css')
            with open(styles, 'r', encoding='utf-8') as styles:
                return Template(file.read()).render({'styles': styles.read()})
    elif request.method == 'POST':
        db = Database('user.db')
        url = 'https://static-maps.yandex.ru/1.x/?'
        pts = []
        res = []
        try:
            db.con = sqlite3.connect(db.address)
            db.cur = db.con.cursor()
            res = db.cur.execute(f'SELECT status, home_geopos, work_geopos, school_geopos FROM profile;').fetchall()
            print(res)
        except Exception as e:
            print(e)
        for i in range(len(res)):
            if res[i][0] == 'результат тестирования(+)':
                if res[i][1]:
                    pts.append(res[i][1])
                    pts.append(res[i][2])
                    pts.append(res[i][3])
        print('pts: ', pts)
        cur_geoloc = request.form['position']
        print(cur_geoloc)
        if cur_geoloc[5].isalpha():
            ll = ','.join(geocode(cur_geoloc)['Point']['pos'].split())
        else:
            ll = ','.join(reversed(list(cur_geoloc.split(', '))))
        print(ll)
        url += 'll=' + ll + '&'
        print(url)
        url += 'l=map&'
        url += 'spn=0.0055,0.0055'
        url += '&size=650,450'
        url += '&pt='
        for i in range(len(pts)):
            a = ','.join(reversed(list(pts[i].split(', '))))
            url += f'{a},pm2blm'
            url += '~'
        url += f'{ll},pm2rdm'
        print(url)
        resp = requests.request('GET', url)
        img = resp.content
        print(resp)
        lll = geocode(ll)
        envelope = lll["boundedBy"]["Envelope"]
        l, b = map(float, envelope["lowerCorner"].split(" "))
        r, t = map(float, envelope["upperCorner"].split(" "))
        d = lonlat_distance((l, b), (r, t))
        print('d =', d)
        chance = ((len(pts) * 29) / d) * 100
        print('chance =', chance)
        unic = random.randint(1, 100)
        map_file = rf"static\images\map{unic}.png"
        try:
            with open(map_file, "wb") as file:
                file.write(img)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
        res = redirect(url_for('img'))
        res.set_cookie('unic', str(unic), max_age=60 * 60 * 24 * 365 * 2)
        res.set_cookie('chance', str(chance), max_age=60 * 60 * 24 * 365 * 2)
        res.set_cookie('geo', ','.join(ll.split(', ')), max_age=60 * 60 * 24 * 365 * 2)
        return res


@app.route('/img', methods=['GET', 'POST'])
def img():
    if request.method == 'GET':
        unic = request.cookies.get('unic')
        chance = float(request.cookies.get('chance'))
        chance = ceil(chance)
        with open(path_to(r'static\auth', 'img.html'), 'r', encoding='utf-8') as file:
            styles = path_to(r'static\css', 'styles1.css')
            with open(styles, 'r', encoding='utf-8') as styles:
                res = Template(file.read()).render(
                    {'styles': styles.read(),
                     'src': path_to(r'static\images', f'map{unic}.png'), 'chance': chance})
                return res
    elif request.method == 'POST':
        pass


@app.route('/nearest_choice', methods=['GET', 'POST'])
def nearest_choice():
    unic1 = request.cookies.get('unic1')
    map_file = rf"static\images\mapc{unic1}.png"
    if request.method == 'GET':
        url = 'https://search-maps.yandex.ru/v1/?apikey=cc07eedd-a85f-455b-a13c-c562f847c953'
        url += f"&text={quote(request.cookies.get('kind'))}"
        url += '&lang=ru_RU'
        db = Database('user.db')
        name = request.cookies.get('email')
        ll = request.cookies.get('geo')
        print(ll, 11111111111111111111111)
        url += f'&ll={ll}'
        url += '&spn=0.0055,0.0055'
        url += '&results=5'
        print(url)
        resp = requests.request('GET', url)
        resp = resp.content
        resp = json.loads(resp)
        resp = resp['features']
        pts = []
        for i in range(len(resp)):
            pts.append(resp[i]['geometry']['coordinates'])
        url = 'https://static-maps.yandex.ru/1.x/?'
        url += 'll=' + ll + '&'
        url += 'l=map&'
        url += 'spn=0.006,0.006'
        url += '&size=650,450'
        url += '&pt='
        for i in range(len(pts)):
            url += f'{",".join((str(x) for x in pts[i]))},pm2dgm'
            url += '~'
        url += f'{ll},pm2rdm'
        ll = list(ll.split(','))
        polygon = ''
        polygon += f'{float(ll[0]) - 0.006},{float(ll[1]) - 0.004},'
        polygon += f'{float(ll[0]) - 0.006},{float(ll[1]) + 0.004},'
        polygon += f'{float(ll[0]) + 0.006},{float(ll[1]) + 0.004},'
        polygon += f'{float(ll[0]) + 0.006},{float(ll[1]) - 0.004},'
        polygon += f'{float(ll[0]) - 0.006},{float(ll[1]) - 0.004}'
        url += '&pl=c:40e0d0AA,f:9cf0e750,w:5,'
        url += polygon
        print(url)
        resp = requests.request('GET', url)
        img = resp.content
        try:
            with open(map_file, "wb") as file:
                file.write(img)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
        with open(path_to(r'static\auth', 'nearest_choice.html'), 'r', encoding='utf-8') as file:
            styles = path_to(r'static\css', 'styles1.css')
            with open(styles, 'r', encoding='utf-8') as styles:
                res = Template(file.read()).render({'styles': styles.read(), 'src': map_file})
                return res
    elif request.method == 'POST':
        kind = request.form['kind']
        res = redirect(url_for(f'nearest_choice'))
        res.set_cookie('kind', kind, max_age=60 * 60 * 24 * 365 * 2)
        unic1 = random.randint(1, 100)
        res.set_cookie('unic1', str(unic1), max_age=60 * 60 * 24 * 365 * 2)
        return res


@app.route('/make_path', methods=['GET', 'POST'])
def make_path():
    if request.method == 'GET':
        with open(path_to(r'static\auth', 'path_choice.html'), 'r', encoding='utf-8') as file:
            styles = path_to(r'static\css', 'styles1.css')
            with open(styles, 'r', encoding='utf-8') as styles:
                res = Template(file.read()).render({'styles': styles.read()})
                return res
    elif request.method == 'POST':
        print(1)
        mode = request.form['mode']
        print(mode)
        origin = request.form['origin']
        print(origin)
        print(request.form['destination'])
        destination = request.form['destination']
        print(destination)
        if origin[5].isalpha():
            origin = ','.join(geocode(origin)['Point']['pos'].split())
        else:
            origin = ','.join(reversed(list(origin.split(', '))))
        print(origin)
        if destination[5].isalpha():
            destination = ','.join(geocode(destination)['Point']['pos'].split())
        else:
            destination = ','.join(reversed(list(destination.split(', '))))
        print(destination)
        coords = find_line('car' if mode.lower() == 'автомобиль' else 'bicycle', origin, destination)[:100]
        url = 'https://static-maps.yandex.ru/1.x/?l=map&pl='
        for i in range(len(coords)):
            url += f'{coords[i][0]},{coords[i][1]}'
            if i != len(coords) - 1:
                url += ','
        print(url)
        resp = requests.request('GET', url)
        img = resp.content
        unic2 = random.randint(1, 100)
        map_file = rf"static\images\mapa{unic2}.png"
        try:
            with open(map_file, "wb") as file:
                file.write(img)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
        res = redirect(url_for('path'))
        res.set_cookie('unic2', str(unic2), max_age=60 * 60 * 24 * 365 * 2)
        return res


@app.route('/path')
def path():
    unic2 = request.cookies.get('unic2')
    map_file = rf"static\images\mapa{unic2}.png"
    with open(path_to(r'static\auth', 'path.html'), 'r', encoding='utf-8') as file:
        styles = path_to(r'static\css', 'styles1.css')
        with open(styles, 'r', encoding='utf-8') as styles:
            res = Template(file.read()).render(
                {'styles': styles.read(), 'src': path_to(r'static\images', f'mapa{unic2}.png')})
            return res


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
