import logging
from flask import Blueprint, jsonify, request
from common.database.nosql.mongodb import ProductDAO

# Define the blueprint: 'control', set its url prefix: app.url/animals/actions
control = Blueprint('control', __name__, url_prefix='/animals/actions')

ProductWrappers = {}


# Set the route and accepted methods
@control.route('/', methods=['GET'])
def get_all_actions_data():
    ret_val = {}
    ProductWrappers.clear()

    # Refresh ProductWrappers
    for product in ProductDAO.get_actions_app_names():
        ret_val[product] = get_product_dao(product).get_app_actions()

    return jsonify(ret_val)


@control.route('/<product>', methods=['GET'])
def get_product_actions_data(product):
    current_actions = get_product_dao(product).get_app_actions()
    if not current_actions:
        current_actions = {}
    return jsonify(current_actions)


@control.route('/<product>/start', methods=['GET'])
def start_product_application(product):
    send_actions_to_store(product, {'status': 'start'}, False)
    return '', 200


@control.route('/<product>/stop', methods=['GET'])
def stop_product_application(product):
    send_actions_to_store(product, {'status': 'stop'}, False)
    return '', 200


@control.route('/<product>', methods=['POST'])
def set_action(product):

    return_code = 200
    try:

        update = bool(request.args.get('update'))
        new_actions = request.get_json(silent=True)
        send_actions_to_store(product, new_actions, update)

    except Exception as ex:
        logging.error(ex)

        # Return 500 - Internal Server Error
        return_code = 500

    return '', return_code


def send_actions_to_store(product, actions, update):
    if update:
        get_product_dao(product).update_app_actions(actions)
    else:
        get_product_dao(product).set_app_actions(actions)


def get_product_dao(product_name):
    if product_name not in ProductWrappers:
        ProductWrappers[product_name] = ProductDAO(product_name)
    return ProductWrappers[product_name]
