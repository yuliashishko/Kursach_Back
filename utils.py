from flask import make_response


def make_resp(message, status):
    resp = make_response(message, status)
    resp.headers['Content-type'] = 'application/json; charset=utf-8'
    return resp


def check_keys(dct, keys):
    return all(key in dct for key in keys)


def check_all_keys_in_dict(dct, keys):
    return all(key in keys for key in dct.keys())


def check_time_in_times(times, curr):
    return any(map(lambda s: (s.start <= curr.start <= s.end or curr.start <= s.start <= curr.end), times))
