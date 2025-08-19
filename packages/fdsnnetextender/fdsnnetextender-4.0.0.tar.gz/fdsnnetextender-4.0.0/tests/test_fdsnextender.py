import pytest
from fdsnnetextender import FdsnNetExtender
from pprint import pprint

myextender = FdsnNetExtender()


def test_extender_YP_2014_bad():
    """
    Test some common FDSN codes and years
    """
    with pytest.raises(ValueError):
        myextender.extend("YP", "2014-")


def test_extender_ZO_2013():
    """
    Test some common FDSN codes and years
    """
    assert myextender.extend("ZO", "2019") == "ZO2018"


def test_extender_permanent():
    """
    Test some common FDSN codes and years
    """
    assert myextender.extend("FR", "2013-01-01") == "FR"


def test_extender_ZT_2016():
    """
    Test some common FDSN codes and years
    """
    assert myextender.extend("YP", "2013-01-01") == "YP2012"


def test_before_network():
    with pytest.raises(ValueError):
        myextender.extend("YP", "1912-01-01")
