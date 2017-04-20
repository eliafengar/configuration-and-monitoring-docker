# Import flask dependencies
from flask import Blueprint, jsonify
from common.database.nosql.mongodb import ProductDAO

# Define the blueprint: 'monitor', set its url prefix: app.url/animals/monitor
monitor = Blueprint('monitor', __name__, url_prefix='/animals/monitor')

ProductWrappers = {}


# Set the route and accepted methods
@monitor.route('/', methods=['GET'])
def all_monitor_data():
    ret_val = {}
    ProductWrappers.clear()

    # Refresh ProductWrappers
    for product in ProductDAO.get_stats_app_names():
        ret_val[product] = get_product_dao(product).get_app_stats()

    return jsonify(ret_val)


@monitor.route('/<product>', methods=['GET'])
def get_monitor_data(product):
    current_monitoring = get_product_dao(product).get_app_stats()
    if not current_monitoring:
        current_monitoring = {}
    return jsonify(current_monitoring)


def get_product_dao(product_name):
    if product_name not in ProductWrappers:
        ProductWrappers[product_name] = ProductDAO(product_name)
    return ProductWrappers[product_name]
