from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy_filters import apply_filters


app = Flask(__name__, template_folder='./templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    links = db.relationship('Long', backref='user')

    def __init__(self, nickname, password):
        self.nickname = nickname
        self.password = password


class Long(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_link = db.Column(db.String(1000), nullable=False)
    short = db.relationship('Short', backref='long', uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, long_link, user):
        self.long_link = long_link
        self.user = user


class Short(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_link = db.Column(db.String(1000), unique=True, nullable=False)
    long_id = db.Column(db.Integer, db.ForeignKey('long.id'), unique=True)

    def __init__(self, short_link, long):
        self.short_link = short_link
        self.long = long


class Operations:
    db = None
    tables = None

    def __init__(self, db, tables):
        self.db = db
        self.tables = tables

    def create_db(self):
        self.db.create_all()

    def return_row(self, ClassName, id):
        return self.tables[ClassName].query.filter_by(id=id).first()

    def return_table(self, ClassName):
        return self.tables[ClassName].query.all()

    def create_long(self, long_link, user):
        element = self.tables['long_link'](long_link, user)
        return element

    def create_short(self, short_link, long):
        element = self.tables['short_link'](short_link, long)
        return element
    
    def create_user(self, nickname, password):
        element = self.tables['user'](nickname, password)
        return element
    
    def inner_join(self, ClassName1, ClassName2, column_name_1, column_name_2):
        records = self.db.session.query(
            self.tables[ClassName1]).\
                join(
                    self.tables[ClassName2], 
                    getattr(
                        self.tables[ClassName1], 
                        column_name_1
                    ) == 
                    getattr(
                        self.tables[ClassName2], 
                        column_name_2
                    )
            )
        return records

    def double_inner_join(self, ClassName1, 
        ClassName2, ClassName3, 
        column_name_1, column_name2, 
        column_name_3
    ):
        records = self.inner_join(
                ClassName1=ClassName1, 
                ClassName2=ClassName2, 
                column_name_1=column_name_1, 
                column_name_2=column_name2
            ).\
        join(
            self.tables[ClassName3], 
            getattr(
                self.tables1[ClassName2], 
                column_name_2
            ) == 
            getattr(
                self.tables[ClassName3], 
                column_name_3
            )
        )


    def appending(self, ClassName, element):
        self.db.session.add(element)
        self.db.session.commit()
        return True

    def remove(self, ClassName, id):  # удаление нашел только по id (оно почему-то не удаляет :( )
        try:
            delete = self.tables[ClassName].query.filter_by(id=id).first()
        except ValueError:
            raise ValueError('Либо такого id нет в базе, либо нет такого класса')
        else:
            self.db.session.delete(delete)
            self.db.session.commit()
            return True

    def update(self, ClassName, id, column_name, value):
        try:
            update = self.tables[ClassName].query.filter_by(id=id).first()
        except ValueError:
            raise ValueError('Либо такого id нет в базе, либо нет такого класса')
        else:
            setattr(update, column_name,
                    value)  
            self.db.session.commit()
            return True

    def filter(self, ClassName, column, value, operation='==', query=None):  # operation может быть не только '==', но и '<', '>'
        if not query:
            query = self.db.session.query(self.tables[ClassName])
        filter_spec = [{'field': column, 'op': operation, 'value': value}]
        result = apply_filters(query, filter_spec)
        return result

    @staticmethod
    def erase(ClassName):
        table = Operations.return_table(ClassName)
        for row in table:
            Operations.remove(ClassName, row.id)
        return True   


if __name__ == '__main__':

    tables = {
        'long_link': Long,
        'short_link': Short,
        'user': User
    }

    ops = Operations(db, tables)
    ops.create_db() 

    long_link = 'https://start.aga=2.181432345.917930497.159991360-1903642690.1595682715' 

    #user = ops.create_user('Nick', '12345')
    user = ops.filter('user', 'nickname', 'Nick')[0]

    print(user)

    long = ops.create_long(long_link=long_link, user=user)

    short_link = 'https://bit.ly/3tNe2dZ'

    short = ops.create_short(short_link=short_link, long=long)

    #ops.appending('user', user)
    ops.appending('long_link', long)
    ops.appending('short_link', short)

    for sample in ops.return_table('long_link'):
        print(sample.id, sample.long_link, sample.user_id)

    print('-------')

    for sample in ops.return_table('short_link'):
        print(sample.id, sample.short_link, sample.long_id)
