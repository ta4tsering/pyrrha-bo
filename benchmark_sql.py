from config import TestConfig
import os
from sqlalchemy import text
import flask
import time


from app import create_app, db
from app.models import Role, User, WordToken

basedir = os.path.abspath(os.path.dirname(__file__))
test_configs = []


class SQLiteConfig(TestConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-benchmark.sqlite')


class MySQLConfig(TestConfig):
    SQLALCHEMY_DATABASE_URI = os.path.join('mysql://ppa:ppa@localhost/benchmark')


def login(client, username, password):
    req = client.post('/account/login', data=dict(
        email=username,
        password=password
    ), follow_redirects=True)


def clear(app: flask.Flask) -> None:
    with app.app_context():
        db.drop_all()
    del app


def create(config) -> flask.Flask:
    app = create_app(config)
    # We create all cli to check that it does not overwrite anything
    with app.app_context():
        db.create_all()
        db.session.commit()
        Role.add_default_roles()
        User.add_default_users()
    return app


def create_corpus(client):
    req = client.post("/corpus/new", data=POST_DATA, follow_redirects=False)
    # We do not want to see the next page


def read_corpus(client):
    req = client.get("/corpus/1/tokens/edit?limit=100")


def get_token(client):
    for attr in ["similar", "new_similar"]:
        fun_timer = []
        for _id in range(100):
            token = WordToken.query.get_or_404(_id+1)
            fun_timer.append(-time.time())
            _ = getattr(token, attr)
            fun_timer[-1] += time.time()
        print(attr, sum(fun_timer)/len(fun_timer))


def experience(app: flask.Flask, calls):
    with app.test_client() as client:
        login(client, USERNAME, PASSWORD)
        for call in calls:
            call(client)
    return app


CONFIGS = [SQLiteConfig]#, MySQLConfig]
EXPERIENCES = 100
USERNAME = "ppa-admin@ppa.fr"
PASSWORD = "admin"
POST_DATA = {}
with open(os.path.join(basedir, "app", "configurations", "langs", "old_french", "lemma.txt")) as f:
    POST_DATA["allowed_lemma"] = f.read()
with open(os.path.join(basedir, "app", "configurations", "langs", "old_french", "morph.txt")) as f:
    POST_DATA["allowed_morph"] = f.read()
with open(os.path.join(basedir, "app", "configurations", "langs", "old_french", "POS.txt")) as f:
    POST_DATA["allowed_POS"] = f.read()
with open(os.path.join(basedir, "benchmark.tsv")) as f:
    POST_DATA["tsv"] = f.read()


if __name__ == "__main__":
    for config in CONFIGS:
        timers = []
        for i in range(EXPERIENCES):
            app = create(config)
            start = time.time()
            try:
                experience(app, [create_corpus, read_corpus])
            except Exception as E:
                print(E)
            timers.append(time.time() - start)
            clear(app)
        print(config.__name__, sum(timers)/len(timers))
        print(timers)

"""

        timers = []
        break
        for i in range(EXPERIENCES):
            app = create(config)

            try:
                experience(app, [create_corpus])
                with app.app_context():
                    #  1.836868953704834 without corpus
                    
                    start = time.time()
                    req = db.engine.execute(
                        text(
                            "SELECT wt.*"
                            ", EXISTS("
                                "SELECT cr.id FROM change_record cr WHERE cr.word_token_id = wt.id"
                            ") AS changed "
                            ", ("
                                "SELECT COUNT(wt2.id) FROM word_token wt2 WHERE "
                                "wt2.id != wt.id AND wt2.corpus = wt.corpus AND wt2.form = wt.form AND "
                                "(wt2.lemma = wt.lemma OR wt2.POS = wt.POS OR wt2.morph = wt.morph)"
                            ") AS similar "
                            "FROM word_token wt "
                            "WHERE wt.corpus = '1' "
                            "ORDER BY wt.order_id "
                            "LIMIT 100"
                        )
                    )
                    print(list([
                        dict(data)
                        for data in req.fetchall()
                    ]))
            except Exception as E:
                print(E)
            timers.append(time.time() - start)
            clear(app)
"""

