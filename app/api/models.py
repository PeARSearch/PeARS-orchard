from app import db


# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())


class Urls(Base):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1000))
    title = db.Column(db.String(1000))
    snippet = db.Column(db.String(1000))
    cc = db.Column(db.Boolean)
    pod = db.Column(db.String(1000))
    category = db.Column(db.String(1000))

    def __init__(self,
                 url=None,
                 title=None,
                 snippet=None,
                 cc=False,
                 pod=None,
                 category=None):
        self.url = url
        self.title = title
        self.snippet = snippet
        self.cc = cc
        self.pod = pod
        self.category = category

    def __repr__(self):
        return self.url

    @property
    def serialize(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'cc': self.cc,
            'pod': self.pod,
            'category': self.category
        }


class Pods(Base):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    url = db.Column(db.String(1000))
    description = db.Column(db.String(7000))
    language = db.Column(db.String(1000))
    registered = db.Column(db.Boolean)

    def __init__(self,
                 name=None,
                 url=None,
                 description=None,
                 language=None,
                 registered=False):
        self.name = name
        self.url = url
        self.description = description
        self.language = language

    @property
    def serialize(self):
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'language': self.language,
            'registered': self.registered
        }


