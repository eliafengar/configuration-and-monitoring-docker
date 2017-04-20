# Import the database object (db) from the main application module
from app import db


# Define a base model for other database tables to inherit
class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


# Define a Product model
class Product(Base):
    __tablename__ = 'portal_product'

    # Product Name
    name = db.Column(db.String(128), nullable=False)

    # New instance instantiation procedure
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Product %r>' % self.name

    def to_json(self):
        return dict(name=self.name)


class Project(Base):
    __tablename__ = 'portal_project'

    # Project Name
    name = db.Column(db.String(128), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('portal_product.id'))
    product = db.relationship('Product', backref=db.backref('products', lazy='dynamic'))

    # New instance instantiation procedure
    def __init__(self, name, product=None):
        self.name = name
        self.product = product

    def __repr__(self):
        return '<Project %r>' % self.name

    def to_json(self):
        return dict(name=self.name)


class Map(Base):
    __tablename__ = 'portal_map'

    # Map Name
    name = db.Column(db.String(128), nullable=False)

    project_id = db.Column(db.Integer, db.ForeignKey('portal_project.id'))
    project = db.relationship('Project', backref=db.backref('projects', lazy='dynamic'))

    # New instance instantiation procedure
    def __init__(self, name, project):
        self.name = name
        self.project = project

    def __repr__(self):
        return '<Map %r>' % self.name

    def to_json(self):
        return dict(name=self.name)
