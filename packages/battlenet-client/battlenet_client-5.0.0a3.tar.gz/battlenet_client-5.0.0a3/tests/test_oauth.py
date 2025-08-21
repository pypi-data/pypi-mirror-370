import pytest

from src.battlenet_client.constants import VALID_REGIONS
from src.battlenet_client.oauth import user_info, token_validation
from src.battlenet_client.exceptions import BNetRegionNotFoundError

from tests.constants import INVALID_REGIONS


@pytest.mark.parametrize('region_tag', VALID_REGIONS)
def test_user_info(region_tag):
    data = user_info(region_tag, locale='enus')
    assert isinstance(data, tuple)
    assert isinstance(data[0], str)
    if region_tag == 'cn':
        assert data[0] == "https://www.battlenet.com.cn/oauth/userinfo"
    elif region_tag in ('tw', 'kr'):
        assert data[0] == f"https://apac.battle.net/oauth/userinfo"
    else:
        assert data[0] == f'https://{region_tag.lower()}.battle.net/oauth/userinfo'
    assert 'locale' in data[1]
    assert data[1]['locale'] == 'en_US'


@pytest.mark.parametrize('region_tag', INVALID_REGIONS)
def test_user_info_invalid_region(region_tag):
    with pytest.raises(BNetRegionNotFoundError):
        user_info(region_tag, locale='enus')


@pytest.mark.parametrize('region_tag', VALID_REGIONS)
def test_token_validation(region_tag):
    token = 'my_good_token_1234'
    data = token_validation(region_tag, token, locale='enus')
    assert isinstance(data, tuple)
    assert isinstance(data[0], str)
    if region_tag == 'cn':
        assert data[0] == "https://www.battlenet.com.cn/oauth/check_token"
    elif region_tag in ('tw', 'kr'):
        assert data[0] == f"https://apac.battle.net/oauth/check_token"
    else:
        assert data[0] == f'https://{region_tag.lower()}.battle.net/oauth/check_token'
    assert isinstance(data[1], dict)
    assert 'locale' in data[1]
    assert 'token' in data[1]
    assert data[1]['locale'] == 'en_US'


@pytest.mark.parametrize('region_tag', INVALID_REGIONS)
def test_token_validation_invalid_region(region_tag):
    with pytest.raises(BNetRegionNotFoundError):
        token = 'my_good_token_1234'
        token_validation(region_tag, token, locale='enus')
