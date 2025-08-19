import random
from uuid import uuid4


def get_uuid():
    return uuid4().hex


def get_id(prefix, length):
    return prefix + "".join(random.choices(uuid4().hex, k=length)).upper()


def get_annotation_id():
    return get_id("", length=10)


def get_base_id():
    return get_id("", length=4)


def get_layer_id():
    return get_id("", length=4)


def get_initial_pecha_id():
    return get_id(prefix="I", length=8)
