import logging
from flask import Blueprint, jsonify, request
from common.database.nosql.mongodb import ProductDAO

# Define the blueprint: 'config', set its url prefix: app.url/animals/config
config = Blueprint('config', __name__, url_prefix='/animals/config')

ProductWrappers = {}


# Set the route and accepted methods
@config.route('/', methods=['GET'])
def get_all_config_data():
    ret_val = {}
    ProductWrappers.clear()

    # Refresh ProductWrappers
    for product in ProductDAO.get_configured_app_names():
        ret_val[product] = get_product_dao(product).get_app_config()

    return jsonify(ret_val)


@config.route('/<product>', methods=['GET'])
def get_product_config_data(product):
    current_config = get_product_dao(product).get_app_config()
    if not current_config:
        current_config = {}
    return jsonify(current_config)


@config.route('/<product>', methods=['POST', 'PUT'])
def store_product_config_data(product):
    return_code = 200
    try:

        update = bool(request.args.get('update'))
        new_config = request.get_json(silent=True)
        if update:
            get_product_dao(product).update_app_config(new_config)
        else:
            get_product_dao(product).set_app_config(new_config)

    except Exception as ex:
        logging.error(ex)

        # Return 500 - Internal Server Error
        return_code = 500

    return '', return_code


def get_product_dao(product_name):
    if product_name not in ProductWrappers:
        ProductWrappers[product_name] = ProductDAO(product_name)
    return ProductWrappers[product_name]
