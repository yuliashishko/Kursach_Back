import datetime

from pip._vendor import requests
from pip._vendor.requests import post, get

print(post('http://localhost:5000/couriers',
           json=
           {
               "data": [
                   {
                       "courier_id": 1,
                       "courier_type": "foot",
                       "regions": [1, 2, 3],
                       "working_hours": ["11:35-14:05", "09:00-11:00"]
                   },
                   {
                       "courier_id": 2,
                       "courier_type": "bike",
                       "regions": [22],
                       "working_hours": ["09:00-18:00"]
                   },
                   {
                       "courier_id": 3,
                       "courier_type": "car",
                       "regions": [12, 22, 23, 33],
                       "working_hours": []
                   },

               ]
           }).json())


print(requests.post('http://localhost:5000/orders', json=
{
    "data": [
        {
            "order_id": 1,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 2,
            "weight": 15,
            "region": 33,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 3,
            "weight": 0.01,
            "region": 23,
            "delivery_hours": ["09:00-12:00", "16:00-21:30"]
        },
        {
            "order_id": 4,
            "weight": 20.01,
            "region": 22,
            "delivery_hours": ["09:00-12:00", "16:00-21:30"]
        }]
}))
print(requests.post('http://localhost:5000/orders/assign', json=
{
    'courier_id': 2
}).json())

print(requests.patch('http://localhost:5000/couriers/1', json=
{
    'regions': [1, 2, 3]
}).json())

print(requests.post('http://localhost:5000/orders/complete', json=
{
    "courier_id": 1,
    "order_id": 5,
    "complete_time": "2021-03-28T16:30:15.089Z"
}).json())
print(requests.get('http://localhost:5000/couriers/1').json())
