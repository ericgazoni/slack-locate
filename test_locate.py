from locate import app, db
from pytest import fixture


@fixture(scope='function')
def client():
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    app.config['SLACK_TOKEN'] = 'gIkuvaNzQIHg97ATvDxqgjtO'
    db.create_all()
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
            'text': '94070',
            'response_url': 'https://hooks.slack.com/commands/1234/5678'}


def test_post_location_simple(client, payload):
    payload['text'] = 'Paris'
    r = client.post('/', data=payload)
    assert r.status_code == 200
