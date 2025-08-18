from cmeta import (
    parse_cmeta,
    to_cmeta,
    model_to_compact_json,
    compact_json_to_model,
    model_to_extended_json,
    extended_json_to_model,
)

CMETA_TEXT = """Webshop[Contains all webshop data]:
  users[Contains all registered users]:
    * user_id<int>[Unique ID of the user]
    * name<string>[Full name of the user]
    * email<string>[Email address]
  orders[Customer orders]:
    * id<int>[Order id]
    * total<double>[Total amount]
    * created_at<timestamp>[When created]
"""


def test_cmeta_roundtrip():
    m = parse_cmeta(CMETA_TEXT)
    back = to_cmeta(m)
    assert "Webshop" in back
    assert "* user_id<int>[Unique ID of the user]" in back


def test_compact_json_roundtrip():
    m = parse_cmeta(CMETA_TEXT)
    cj = model_to_compact_json(m)
    m2 = compact_json_to_model(cj)
    assert to_cmeta(m2).strip() == to_cmeta(m).strip()


def test_extended_json_roundtrip():
    m = parse_cmeta(CMETA_TEXT)
    ej = model_to_extended_json(m)
    m2 = extended_json_to_model(ej)
    # order-insensitive check
    assert sorted([t.name for t in m2.lakes[0].tables]) == sorted(
        [t.name for t in m.lakes[0].tables]
    )
