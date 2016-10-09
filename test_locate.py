from application import app, db, parse_date, parse_command
from pytest import fixture
import datetime
import json

TODAY = datetime.date.today()
TOMORROW = datetime.date.today() + datetime.timedelta(days=1)


@fixture(scope='function')
def client(request):
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    app.config['SLACK_TOKEN'] = 'gIkuvaNzQIHg97ATvDxqgjtO'
    db.create_all()

    def finalize():
        db.drop_all()
    request.addfinalizer(finalize)

    return app.test_client()


@fixture
def payload():
    return {'token': 'gIkuvaNzQIHg97ATvDxqgjtO',
            'team_id': 'T0001',
            'team_domain': 'example',
            'channel_id': 'C2147483705',
            'channel_name': 'test',
            'user_id': 'U2147483697',
            'user_name': 'Steve',
            'command': '/locate',
            'response_url': 'https://hooks.slack.com/commands/1234/5678'}


def test_post_location_simple(client, payload):
    payload['text'] = 'set Paris'
    r = client.post('/', data=payload)
    assert r.status_code == 200


def test_locate_friend(client, payload):
    payload['text'] = 'set Paris'
    r = client.post('/', data=payload)
    assert r.status_code == 200

    payload['text'] = 'Steve'
    r = client.post('/', data=payload)
    assert r.status_code == 200
    message = json.loads(r.data.decode('utf-8'))
    assert 'steve' in message['text']
    assert 'Paris' in message['text']

    payload['text'] = '@Steve'
    r = client.post('/', data=payload)
    assert r.status_code == 200
    message = json.loads(r.data.decode('utf-8'))
    assert 'steve' in message['text']
    assert 'Paris' in message['text']


def test_locate_no_friend(client, payload):
    payload['text'] = 'Steve'
    r = client.post('/', data=payload)
    assert r.status_code == 200
    message = json.loads(r.data.decode('utf-8'))
    assert 'steve' in message['text']
    assert 'Paris' not in message['text']


def test_locate_friend_ordered(client, payload):
    payload['text'] = 'set Paris'
    r = client.post('/', data=payload)
    assert r.status_code == 200

    payload['text'] = 'set Brussels'
    r = client.post('/', data=payload)
    assert r.status_code == 200

    payload['text'] = 'Steve'
    r = client.post('/', data=payload)
    assert r.status_code == 200
    message = json.loads(r.data.decode('utf-8'))
    assert 'steve' in message['text']
    assert 'Brussels' in message['text']


def test_parse_date():
    assert parse_date('today') == TODAY
    assert parse_date('tomorrow') == TOMORROW
    assert parse_date('2016-01-18') == datetime.date(2016, 1, 18)


def test_parse_command_full():
    parsed = parse_command('set Paris today to tomorrow')
    assert parsed['place'] == 'paris'
    assert parsed['start'] == TODAY
    assert parsed['end'] == TOMORROW


def test_parse_command_place_only():
    parsed = parse_command('set Paris ')
    assert parsed['place'] == 'paris'
    assert parsed['start'] is None
    assert parsed['end'] is None


def test_parse_command_start():
    parsed = parse_command('set Paris tomorrow')
    assert parsed['place'] == 'paris'
    assert parsed['start'] == TOMORROW
    assert parsed['end'] is None
