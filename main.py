from flask import Flask, request, jsonify
from sqlalchemy.testing.plugin.plugin_base import post
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from data import db_session
from data.courier import Courier
from data.delivery_hour import DeliveryHour
from data.order import Order
from data.region import Region
from data.working_hour import WorkingHour
from utils import make_resp, check_keys, check_all_keys_in_dict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flag_is_here'



@app.route('/couriers', methods=['POST'])
def post_couriers():
    session = db_session.create_session()
    get_data = request.json
    validation_error = []
    ids = []
    for i in get_data['data']:
        if not check_keys(i, ('courier_id', 'courier_type', 'regions', 'working_hours')) or \
                not check_all_keys_in_dict(i, ('courier_id', 'courier_type', 'regions', 'working_hours')):
            validation_error.append({"id": i['courier_id']})
        else:
            ids.append({"id": i['courier_id']})
            regions = []
            for j in i['regions']:
                region = Region(
                    region=j,
                    courier_id=i['courier_id']
                )
                regions.append(region)
            working_hours = []
            for j in i['working_hours']:
                working_hour = WorkingHour(
                    working_hour=j,
                    courier_id=i['courier_id']
                )
                working_hours.append(working_hour)
            courier = Courier(
                courier_id=i['courier_id'],
                courier_type=i['courier_type'],
                regions=regions,
                working_hours=working_hours
            )
            session.add(courier)
            session.commit()
    if validation_error:
        return make_resp(
            {
                'validation_error': {
                    "couriers": validation_error
                }
            }, 400)
    else:
        return make_resp(
            {
                "couriers": ids
            }, 201)


@app.route('/couriers/<int:id>', methods=['PATCH'])
def patch_courier(id):
    session = db_session.create_session()
    get_data = request.json
    if not check_all_keys_in_dict(get_data, ('courier_id', 'courier_type', 'regions', 'working_hours')):
        return make_resp('', 400)
    courier = session.query(Courier).filter(Courier.courier_id == id).first()
    if courier:
        if 'courier_type' in get_data.keys():
            session.query(Courier).filter(Courier.courier_id == id).update({
                'courier_type': get_data['courier_type']
            }
            )
        if 'regions' in get_data.keys():
            courier.update_regions(get_data['regions'], session)
        if 'working_hours' in get_data.keys():
            courier.update_working_hours(get_data['working_hours'], session)
        session.commit()
        courier = session.query(Courier).filter(Courier.courier_id == id).first()
        courier_type = courier.courier_type
        regions = [i.region for i in courier.regions]
        working_hours = [i.working_hour for i in courier.working_hours]
        return make_resp(
            {
                "courier_id": id,
                "courier_type": courier_type,
                "regions": regions,
                "working_hours": working_hours
            }
            , 200)
    else:
        return make_resp('', 400)


@app.route('/orders', methods=['POST'])
def post_orders():
    session = db_session.create_session()
    data = request.json
    validation_error = []
    ids = []
    for i in data['data']:
        if not check_keys(i, ('order_id', 'weight', 'region', 'delivery_hours')) or \
                not check_all_keys_in_dict(i, ('order_id', 'weight', 'region', 'delivery_hours')):
            validation_error.append({"id": i['order_id']})
        else:
            order = session.query(Order).filter(Order.order_id == i['order_id']).first()
            if order:
                session.delete(order)
                session.commit()
            ids.append({"id": i['order_id']})
            delivery_hours = []
            for j in i['delivery_hours']:
                delivery_hour = DeliveryHour(
                    delivery_hour=j,
                    order_id=i['order_id']
                )
                delivery_hours.append(delivery_hour)
            order = Order(
                order_id=i['order_id'],
                weight=i['weight'],
                region=i['region'],
                delivery_hours=delivery_hours
            )
            session.add(order)
            session.commit()
    if validation_error:
        return make_resp(
            {
                'validation_error': {
                    "orders": validation_error
                }
            }, 400)
    else:
        return make_resp(
            {
                "orders": ids
            }, 201)


@app.route("/couriers/<int:id>", methods=["GET"])
def get_courier(id):
    session = db_session.create_session()
    courier = session.query(Courier).filter(Courier.courier_id == id).first()
    if courier:
        courier_type = courier.courier_type
        regions = [i.region for i in courier.regions]
        working_hours = [i.working_hour for i in courier.working_hours]
        rating = courier.get_rating(session)
        earnings = courier.get_earning(session)
        return make_resp({"courier_id": id,
                          "courier_type": courier_type,
                          "regions": regions,
                          "working_hours": working_hours,
                          "rating": rating,
                          "earnings": earnings
                          }, 200)
    else:
        return make_resp({'Message': "Courier not found"}, 400)


def main():
    db_session.global_init("db/yaschool")
    app.run()


main()
