import pytest

from releaserabbit import get_new_version


def test_component_bump():
    assert get_new_version('1.2.3', '4.5.6') == '4.5.6'
    assert get_new_version('1.2.3', 'patch') == '1.2.4'
    assert get_new_version('1.2.3', 'minor') == '1.3.0'
    assert get_new_version('1.2.3', 'major') == '2.0.0'
    assert get_new_version('81.999.50', 'minor') == '81.1000.0'
    with pytest.raises(ValueError):
        get_new_version('80.999.50', 'nonsense')
