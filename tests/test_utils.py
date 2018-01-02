import datetime
import time

from cpython_stats.utils import cache_response


def test_ivalidator():
    # GIVEN

    @cache_response(datetime.timedelta(seconds=0.5))
    def function():
        return datetime.datetime.now()

    # WHEN

    result = function()
    result2 = function()
    time.sleep(0.5)
    result3 = function()

    # Then

    assert result == result2
    assert result != result3
