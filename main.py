from flask import Flask, request, jsonify
from sqlalchemy.testing.plugin.plugin_base import post
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from data import db_session
from data.courier import Courier
from data.region import Region
from data.working_hour import WorkingHour
from utils import make_resp, check_keys, check_all_keys_in_dict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flag_is_here'


@app.route('/', methods=['GET'])
def do_huynya():
    return make_resp('Гет-хуйня работает', 200)


@app.route('/', methods=['POST'])
def do_huynya2():
    return make_resp('Пост-хуйня работает', 201)


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
    if not check_keys(get_data.keys(), ('courier_id', 'courier_type', 'regions', 'working_hours')):
        return make_resp('', 400)
    courier = session.query(Courier).filter(Courier.courier_id == id).first()
    if courier:
        if 'courier_type' in get_data.keys():

        session.query(Courier).filter(Courier.courier_id == id).update(

        )


def main():
    db_session.global_init("db/yaschool")
    app.run()


main()
