import importlib


def test_add_ord_suffix_import():
    module = importlib.import_module("src.bear_utils.time")
    assert hasattr(module, "add_ord_suffix")
    func = module.add_ord_suffix
    assert callable(func)
    assert func(1) == "1st"
    assert func(2) == "2nd"
    assert func(3) == "3rd"
    assert func(4) == "4th"
