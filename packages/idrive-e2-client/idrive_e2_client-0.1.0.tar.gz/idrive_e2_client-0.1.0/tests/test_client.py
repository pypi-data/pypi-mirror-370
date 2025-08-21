import aiohttp
import pytest
from aioresponses import aioresponses

from idrive_e2 import IDriveE2Client, InvalidAuth, CannotConnect

API_URL = "https://api.idrivee2.com/api/service/get_region_end_point"


@pytest.mark.asyncio
async def test_get_region_endpoint_success():
    payload = {
        "resp_code": 0,
        "resp_msg": "Success",
        "domain_name": "m2s0.tx11.idrivee2-3.com",
    }
    async with aiohttp.ClientSession() as sess:
        client = IDriveE2Client(sess)
        with aioresponses() as m:
            m.post(API_URL, payload=payload, status=200)
            endpoint = await client.get_region_endpoint("AKIA...")
            assert endpoint == "https://m2s0.tx11.idrivee2-3.com"


@pytest.mark.asyncio
async def test_get_region_endpoint_invalid_auth_negative_code():
    payload = {
        "resp_code": -100,
        "resp_msg": "Invalid Access Key",
        "domain_name": "m2s0.tx11.idrivee2-3.com",
    }
    async with aiohttp.ClientSession() as sess:
        client = IDriveE2Client(sess)
        with aioresponses() as m:
            m.post(API_URL, payload=payload, status=200)
            with pytest.raises(InvalidAuth) as exc:
                await client.get_region_endpoint("badkey")
            assert "API error -100: Invalid Access Key" in str(exc.value)


@pytest.mark.asyncio
async def test_get_region_endpoint_missing_resp_code():
    payload = {
        "resp_msg": "Something went wrong",
        "domain_name": "m2s0.tx11.idrivee2-3.com",
    }
    async with aiohttp.ClientSession() as sess:
        client = IDriveE2Client(sess)
        with aioresponses() as m:
            m.post(API_URL, payload=payload, status=200)
            with pytest.raises(CannotConnect) as exc:
                await client.get_region_endpoint("key")
            assert "Missing resp_code" in str(exc.value)


@pytest.mark.asyncio
async def test_get_region_endpoint_wrong_type_resp_code():
    payload = {
        "resp_code": "oops",
        "resp_msg": "Bad type",
        "domain_name": "m2s0.tx11.idrivee2-3.com",
    }
    async with aiohttp.ClientSession() as sess:
        client = IDriveE2Client(sess)
        with aioresponses() as m:
            m.post(API_URL, payload=payload, status=200)
            with pytest.raises(CannotConnect) as exc:
                await client.get_region_endpoint("key")
            assert "Unexpected resp_code type" in str(exc.value)


@pytest.mark.asyncio
async def test_get_region_endpoint_unexpected_positive_code():
    payload = {
        "resp_code": 5,
        "resp_msg": "Strange code",
        "domain_name": "m2s0.tx11.idrivee2-3.com",
    }
    async with aiohttp.ClientSession() as sess:
        client = IDriveE2Client(sess)
        with aioresponses() as m:
            m.post(API_URL, payload=payload, status=200)
            with pytest.raises(CannotConnect) as exc:
                await client.get_region_endpoint("key")
            assert "Unexpected resp_code value: 5" in str(exc.value)


@pytest.mark.asyncio
async def test_get_region_endpoint_http_error():
    async with aiohttp.ClientSession() as sess:
        client = IDriveE2Client(sess)
        with aioresponses() as m:
            m.post(API_URL, status=500)
            with pytest.raises(CannotConnect):
                await client.get_region_endpoint("key")


@pytest.mark.asyncio
async def test_get_region_endpoint_missing_domain_name():
    payload = {
        "resp_code": 0,
        "resp_msg": "OK",
    }  # no domain_name
    async with aiohttp.ClientSession() as sess:
        client = IDriveE2Client(sess)
        with aioresponses() as m:
            m.post(API_URL, payload=payload, status=200)
            with pytest.raises(CannotConnect) as exc:
                await client.get_region_endpoint("key")
            assert "Missing domain_name" in str(exc.value)
