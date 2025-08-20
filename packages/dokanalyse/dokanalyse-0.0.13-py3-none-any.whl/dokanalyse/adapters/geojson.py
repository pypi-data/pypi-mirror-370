import logging
import os
from urllib.parse import urlparse
from typing import Dict, Tuple, Union
from pydantic import HttpUrl, FileUrl
from osgeo import ogr
import aiohttp
import asyncio
from async_lru import alru_cache
from .gdal import query_gdal

_LOGGER = logging.getLogger(__name__)
_CACHE_TTL = 86400


async def query_geojson(url: Union[HttpUrl, FileUrl], filter: str, geometry: ogr.Geometry, epsg: int, timeout: int = 30) -> Dict:
    geojson = await _get_geojson(url, timeout)

    if not geojson:
        return None

    return query_gdal('GeoJSON', geojson, filter, geometry, epsg)


@alru_cache(maxsize=32, ttl=_CACHE_TTL)
async def _get_geojson(url: Union[HttpUrl, FileUrl], timeout) -> str:
    if url.scheme == 'file':
        geojson = _load_geojson(url)
    else:
        _, geojson = await _fetch_geojson(url, timeout)

    return geojson


async def _fetch_geojson(url: HttpUrl, timeout) -> Tuple[int, str]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                if response.status != 200:
                    return response.status, None

                json_str = await response.text()

                return 200, json_str
    except asyncio.TimeoutError:
        return 408, None
    except Exception as err:
        _LOGGER.error(err)
        return 500, None


def _load_geojson(file_uri: FileUrl) -> str:
    path = _file_uri_to_path(file_uri)

    try:
        with open(path) as file:
            return file.read()
    except:
        return None


def _file_uri_to_path(file_uri: FileUrl) -> str:
    parsed = urlparse(str(file_uri))

    return os.path.abspath(os.path.join(parsed.netloc, parsed.path))
