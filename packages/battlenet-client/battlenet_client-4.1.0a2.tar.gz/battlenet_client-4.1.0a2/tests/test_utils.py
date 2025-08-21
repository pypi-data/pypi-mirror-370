import pytest
from battlenet_client import utils
from battlenet_client.exceptions import BNetValueError


@pytest.mark.parametrize(
    "value",
    [(1723, 40, 32), [1723, 40, 32], {"gold": 1723, "silver": 40, "copper": 32}],
)
def test_currency_convertor_invalid_type(value):
    with pytest.raises(TypeError):
        utils.currency_convertor(value)


def test_currency_convertor_negative_number():
    with pytest.raises(BNetValueError):
        utils.currency_convertor(-43_23_11)


@pytest.mark.parametrize("value", ["17234032", 17234032])
def test_currency_convertor_str(value):
    value = utils.currency_convertor(value)
    assert isinstance(value, tuple)
    assert value == (1723, 40, 32)


def test_slugify_with_int():
    result = utils.slugify(81)
    assert isinstance(result, int)
    assert result == 81


def test_slugify_with_tuple():
    with pytest.raises(AttributeError):
        # noinspection PyTypeChecker
        utils.slugify((1, 3, 4))


def test_slugify_with_str():
    result = utils.slugify("We'll Be Back")
    assert isinstance(result, str)
    assert result == 'well-be-back'


def test_localize_with_none():
    result = utils.localize(None)
    assert result is None


def test_localize_with_int():
    with pytest.raises(BNetValueError):
        # noinspection PyTypeChecker
        utils.localize(81)


def test_localize_with_aaus():
    with pytest.raises(BNetValueError):
        utils.localize('aaUS')


def test_localize_with_enaa():
    with pytest.raises(BNetValueError):
        utils.localize('enaa')


def test_localize_with_enus():
    result = utils.localize('enUS')
    assert isinstance(result, str)
    assert result == 'en_US'


def test_api_host_cn():
    result = utils.api_host('CN')
    assert result == "https://gateway.battlenet.com.cn"


def test_api_host_us():
    result = utils.api_host('US')
    assert result == "https://us.api.blizzard.com"


def test_auth_host_cn():
    result = utils.auth_host('CN')
    assert result == "https://www.battlenet.com.cn"


def test_auth_host_us():
    result = utils.auth_host('US')
    assert result == "https://us.battle.net"


def test_auth_host_tw():
    result = utils.auth_host('TW')
    assert result == "https://apac.battle.net"


def test_render_host_cn():
    result = utils.render_host('CN')
    assert result == "https://render.worldofwarcraft.com.cn"


def test_render_host_us():
    result = utils.render_host('US')
    assert result == "https://render-us.worldofwarcraft.com"
