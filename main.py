from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from database import *
from LinkCorrector import *
import json
import re


tables = {
    'long_link': Long,
    'short_link': Short,
    'user': User
}

domen_name = 'https://avito-short-test.herokuapp.com/'

ops = Operations(db, tables)
ops.create_db() 
#ops.appending('user', ops.create_user('Nick', '12345'))
#ops.appending('user', ops.create_user('Nick2', '12dq345'))


def check_element(table_name, var_name, column_name):
    find_flag = False
    for element in ops.return_table(table_name):
        if getattr(element, column_name) == var_name:
            find_flag = True
            break
    return find_flag

def long_link_filtering(nickname, link_name):
    find_flag=False
    for element in ops.inner_join(ClassName1='user', ClassName2='long_link', column_name_1='id', column_name_2='user_id'):
        if element.user.nickname == nickname and element.long.long_link == link_name:
            find_flag=True
            break
    return find_flag

@app.route('/', methods=["POST", "GET", 'OPTIONS'])
def index_page():
	return render_template('index.html')

@app.route("/authentication", methods=["POST", "GET", 'OPTIONS'])
def authentication():
    data = request.form
    nickname = request.args.get('nickname') if request.args.get('nickname') is not None else data['nickname']
    password = request.args.get('password') if request.args.get('password') is not None else data['password']
    url = request.args.get('url') if request.args.get('url') is not None else data['url']
    custom_short = request.args.get('short') if request.args.get('short') is not None else data['short']

    find_flag = check_element(
        table_name='user', 
        var_name=nickname, 
        column_name='nickname'
    )
    
    if not find_flag:  #Если не нашли пользователя в БД, то создаем нового пользователя по введенному логину и паролю
        ops.appending(
            ClassName='user', 
            element=ops.create_user(
                nickname=nickname,
                password=password
            )
        )
    else:
        filtered_user = ops.db.session.query(
            tables['user'], 
        ).filter(
            tables['user'].nickname == nickname
        ).filter(
            tables['user'].password == password
        )

        if not len(filtered_user.all()):
            return 'Неверный пароль!'

    if url.find("http://") != 0 and url.find("https://") != 0:
        url = "https://" + url

    find_link_flag = check_element(
        table_name='long_link', 
        var_name=url, 
        column_name='long_link'
    )

    if find_link_flag:
        return json.dumps(
            {
                'nickname': nickname, 
                'long_url': url,
                'short_url': f"{ops.inner_join(ClassName1='long_link', ClassName2='short_link', column_name_1='id', column_name_2='id').all()[0].short.short_link}"
            }
        )
    else:
        if re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url):
            user = ops.filter(ClassName='user', 
                column='nickname', 
                value=nickname,
            )[0]
            
            long = ops.create_long(
                long_link=url, 
                user=user
            )

            if custom_short is not None and len(custom_short):
                short = custom_short
            else:
                short = build_short_link(
                    long_link=url
                )
            
            short_link = domen_name + f'{short}'

            if check_element('short_link', short_link, 'short_link'):
                return 'Такой уникальный ключ уже есть в базе, попробуйте ввести другой или перезагрузите страницу в случае генерации одинакового ключа'

            short_sample = ops.create_short(
                short_link=short_link,
                long=long
            )

            ops.appending(
                ClassName='user', 
                element=user
            )
            
            ops.appending(
                ClassName='long_link', 
                element=long
            )
            
            ops.appending(
                ClassName='short_link', 
                element=short_sample
            )
        
            return json.dumps(
                {
                    'nickname': nickname,
                    'long_url': url,
                    'short_url': short_link
                }
            )

        else:
            return f'Неверный формат url: {url}'

@app.route('/redirecting',  methods=["POST", "GET", 'OPTIONS'])
def redirecting():
    nickname = request.args.get('nickname')
    password = request.args.get('password')
    short_link = request.args.get('short')

    if not check_element(table_name='user', var_name=nickname, column_name='nickname'):
        return f'Пользователь {nickname} еще не пользовался сайтом, сначала создайте ссылку'

    filtered_user = ops.db.session.query(
            tables['user'], 
        ).filter(
            tables['user'].nickname == nickname
        ).filter(
            tables['user'].password == password
        )

    if not len(filtered_user.all()):
        return 'Неверный пароль!'
    
    if re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', short_link) and short_link.find(domen_name) != -1:
        filtered = ops.db.session.query(
            tables['user'], 
            tables['long_link'],
            tables['short_link']
        ).join(
            tables['long_link'],
            tables['user'].id == tables['long_link'].user_id
        ).join(
            tables['short_link'],
            tables['long_link'].id == tables['short_link'].long_id
        ).filter(
            tables['short_link'].short_link == short_link
        ).all()

        if not len(filtered):
            return 'Такой ссылки нет в базе данных'

        result = filtered[0][1].long_link

        return redirect(result)
    
    else:
        return f'Некорректная ссылка, правильная должна содержать имя домена: {domen_name}'

@app.route('/link/<short_link>')
def link():
    pass


if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000)
    