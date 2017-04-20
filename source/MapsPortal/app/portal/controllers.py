# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify

from flask_json import json_response

# Import password / encryption helper tools
from werkzeug import check_password_hash, generate_password_hash

from app.portal.models import Product, Project, Map

# Define the blueprint: 'auth', set its url prefix: app.url/auth
portal = Blueprint('maps', __name__, url_prefix='/portal/maps')


# Set the route and accepted methods
@portal.route('/')
def index():
    prods = Product.query.order_by(Product.name)
    return render_template("portal/index.html", products=prods)


@portal.route('/products/<product>/projects', methods=['GET'])
def get_projects(product):
    product_object = Product.query.filter_by(name=product).first()
    project_objects = Project.query.filter_by(product=product_object).all()
    if len(project_objects) == 1:
        return jsonify([project_objects[0].to_json()])
    return jsonify([obj.to_json() for obj in project_objects])


@portal.route('/products/<product>/projects/<project>/maps', methods=['GET'])
def get_maps(product, project):
    product_object = Product.query.filter_by(name=product).first()
    project_object = Project.query.filter_by(name=project, product=product_object).first()
    map_objects = Map.query.filter_by(project=project_object).all()
    if len(map_objects) == 1:
        return jsonify([map_objects[0].to_json()])
    return jsonify([obj.to_json() for obj in map_objects])
