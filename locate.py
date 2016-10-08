from flask import Flask, request, abort
import re
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SLACK_TOKEN'] = ''
db = SQLAlchemy(app)
api = Api(app)


def parse_command(text):
    mode = text.split()[0]
    if mode == 'set':
        text = ' '.join(text.split()[1:])
        time_regexp = '(?P<place>\S+)( (?P<start>\S+)?( (to|until)? (?P<end>\S+)?){0,1}){0,1}'
        details = re.match(time_regexp, text)
        if details:
            details = details.groupdict()
            print(details)


class Team(db.Model):
    id = db.Column(db.Unicode, primary_key=True)
    domain = db.Column(db.Unicode)


class User(db.Model):
    id = db.Column(db.Unicode, primary_key=True)
    name = db.Column(db.Unicode)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team = db.relationship('Team', backref=db.backref('users'))

    def __repr__(self):
        return '<User {} "{}">'.format(self.id, self.name)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    place = db.Column(db.Unicode, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('locations'))


class LocationService(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('token', type=str)
        parser.add_argument('user_id', type=str)
        parser.add_argument('user_name', type=str)

        parser.add_argument('team_id', type=str)
        parser.add_argument('team_domain', type=str)

        parser.add_argument('text', type=str)

        args = parser.parse_args()

        if args['token'] != app.config['SLACK_TOKEN']:
            abort(403, 'wrong Slack token')

        user = User.query.get(args['user_id'])
        if not user:
            s = db.session
            team = Team(id=args['team_id'], domain=args['team_domain'])
            s.add(team)
            user = User(id=args['user_id'], name=args['user_name'], team=team)
            s.add(user)

api.add_resource(LocationService, '/')

if __name__ == '__main__':
    db.create_all()
    app.run()
