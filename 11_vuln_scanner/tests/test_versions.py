from vulnscan.versions import compare, normalize_dotted, train


def test_compare_cisco_formats():
    assert compare("17.06.04", "17.6.6a") < 0
    assert compare("17.6.6", "17.6.6a") < 0
    assert compare("17.9.4a", "17.9.4a") == 0
    assert compare("9.8(4)15", "9.8.4.20") < 0
    assert compare("9.8(4)45", "9.8.4.20") > 0
    assert compare("15.2(7)E8", "15.2(7)E10") < 0


def test_compare_comware_release():
    assert compare("3208P10", "3507P10") < 0
    assert compare("3507P10", "3507P9") > 0


def test_train_and_normalize():
    assert train("17.06.04") == "17.6"
    assert train("9.8(4)15") == "9.8"
    assert normalize_dotted("17.06.04") == "17.6.4"
