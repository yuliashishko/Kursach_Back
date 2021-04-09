import datetime

from flask import Flask, request, jsonify
from sqlalchemy.testing.plugin.plugin_base import post
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from data import db_session
from data.courier import Courier
from data.delivery_hour import DeliveryHour
from data.order import Order
from data.order_in_progress import OrderInProgress
from data.region import Region
from data.working_hour import WorkingHour
from utils import make_resp, check_keys, check_all_keys_in_dict, check_time_in_times, BASE_COMPLETE_TIME
from waitress import serve
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
                    courier_id=i['courier_id']
                )
                working_hour.set_working_hour(j)
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

        courier = session.query(Courier).filter(Courier.courier_id == id).first()
        courier_type = courier.courier_type
        regions = [i.region for i in courier.regions]
        working_hours = [i.working_hour for i in courier.working_hours]
        courier_orders = courier.orders
        for i in courier_orders:
            if i.order.region not in regions or not check_time_in_times(courier.working_hours,
                                                                        i.order.delivery_hours[0]):
                i.order.is_taken = False
                session.query(OrderInProgress).filter(OrderInProgress.order_id == i.order_id).delete()
        session.commit()
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
                    order_id=i['order_id']
                )
                delivery_hour.set_delivery_hour(j)
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


@app.route("/orders/assign", methods=["POST"])
def order_assign():
    time_now = datetime.datetime.now()
    session = db_session.create_session()
    get_data = request.json
    courier = session.query(Courier).filter(Courier.courier_id == get_data['courier_id']).first()
    if courier:
        weight = {'foot': 10, 'bike': 15, 'car': 50}
        max_weight = weight[courier.courier_type]
        orders_in_progress = courier.orders
        add_weight = max_weight - sum([i.order.weight for i in orders_in_progress if i.complete_time == BASE_COMPLETE_TIME])
        courier_regions = [i.region for i in courier.regions]
        # orders = session.query(Order).filter(Order.weight <= add_weight, Order.region.in_(courier_regions),
        #                                      ~Order.is_taken).limit(add_weight * 100).all()
        if not courier.working_hours or not courier.regions:
            return make_resp(
                {
                    "orders": []
                },
                200)
        time_condition = "("
        region_condition = "("
        for hour in courier.working_hours:
            time_condition += f"(dh.start <= '{hour.end}' and dh.end >= '{hour.start}') or "
        time_condition = time_condition[:-4]
        time_condition += ")"
        for reg in courier.regions:
            region_condition += f"o.region = {reg.region} or "
        region_condition = region_condition[:-4]
        region_condition += ")"
        res = session.execute("select * from orders o "
                              "join delivery_hours dh on o.order_id = dh.order_id  " +
                              "where o.is_taken = 0 and " + time_condition + " and " + region_condition +
                              f" and o.weight <= {weight[courier.courier_type]} group by o.order_id limit {add_weight * 100}").fetchall()
        res_ids = [i[0] for i in res]
        orders = session.query(Order).filter(Order.order_id.in_(res_ids)).all()
        courier_orders = []
        for order in orders:
            if add_weight >= order.weight:
                add_weight -= order.weight
                courier_orders.append(order)
            elif not weight:
                break
        for order in courier_orders:
            order_in_progress = OrderInProgress(
                order_id=order.order_id,
                courier_id=courier.courier_id,
                courier_type=courier.courier_type,
                assign_time=time_now,
                complete_time=BASE_COMPLETE_TIME
            )
            order.is_taken = True
            session.add(order_in_progress)
            session.commit()
        orders = [i for i in courier.orders if i.complete_time == BASE_COMPLETE_TIME]
        if orders:
            assign_time = max(orders, key=lambda s: s.assign_time)
            return make_resp(
                {
                    "orders": [{"id": i.order_id} for i in orders if i.complete_time == BASE_COMPLETE_TIME],
                    "assign_time": assign_time
                },
                200)
        else:
            return make_resp(
                {
                    "orders": []
                },
                200)
    else:
        return make_resp('', 400)


@app.route("/orders/complete", methods=["POST"])
def orders_complete():
    session = db_session.create_session()
    get_data = request.json
    date_time = datetime.datetime.strptime(get_data['complete_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
    if not check_all_keys_in_dict(get_data, ('courier_id', 'order_id', 'complete_time')) or \
            not check_keys(get_data, ('courier_id', 'order_id', 'complete_time')):
        return make_resp('', 400)
    complete_order = session.query(OrderInProgress).filter(OrderInProgress.courier_id == get_data['courier_id'],
                                                           OrderInProgress.order_id == get_data['order_id']).first()
    if complete_order:
        complete_order.complete_time = date_time
        complete_order.set_duration(session)
        complete_id = complete_order.order_id
        session.commit()
        return make_resp(
            {
                "order_id": complete_id
            },
            200)
    return make_resp('', 400)


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
    db_session.global_init("db/yaschool.sqlite")
    app.run(host='0.0.0.0', port="8080")
    #serve(app, host='0.0.0.0', port="8080")


main()
