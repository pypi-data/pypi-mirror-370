import time
import logging
import traceback
from typing import List, Dict, Tuple
from uuid import UUID, uuid4
import asyncio
from socketio import SimpleClient
from osgeo import ogr
from pydash import kebab_case
from .dataset import get_config_ids, get_dataset_type
from .fact_sheet import create_fact_sheet
from .municipality import get_municipality
from .config import get_dataset_config
from .map_image import generate_map_images
from .report import create_pdf
from .blob_storage import create_container, upload_binary
from ..utils.helpers.geometry import create_input_geometry, get_epsg
from ..models.config import DatasetConfig
from ..models import Analysis, ArcGisAnalysis, OgcApiAnalysis, WfsAnalysis, EmptyAnalysis, AnalysisResponse, ResultStatus
from ..utils.constants import DEFAULT_EPSG
from ..utils.correlation_id_middleware import get_correlation_id

_LOGGER = logging.getLogger(__name__)


async def run(data: Dict, sio_client: SimpleClient) -> AnalysisResponse:
    geo_json = data.get('inputGeometry')
    geometry = create_input_geometry(geo_json)
    orig_epsg = get_epsg(geo_json)
    buffer = data.get('requestedBuffer', 0)
    context = data.get('context') or ''
    include_guidance = data.get('includeGuidance', False)
    include_quality_measurement = data.get('includeQualityMeasurement', False)
    include_facts = data.get('includeFacts', True)
    municipality_number, municipality_name = await get_municipality(geometry, DEFAULT_EPSG)

    datasets = await get_config_ids(data, municipality_number)
    correlation_id = get_correlation_id()

    if datasets and correlation_id and sio_client:
        to_analyze = {key: value for (
            key, value) in datasets.items() if value == True}
        sio_client.emit('datasets_counted_api', {'count': len(
            to_analyze), 'recipient': correlation_id})

    tasks: List[asyncio.Task] = []

    async with asyncio.TaskGroup() as tg:
        for config_id, should_analyze in datasets.items():
            task = tg.create_task(_run_analysis(
                config_id, should_analyze, geometry, DEFAULT_EPSG, orig_epsg, buffer,
                context, include_guidance, include_quality_measurement, sio_client))
            tasks.append(task)

    fact_sheet = None

    if include_facts:
        if correlation_id and sio_client:
            sio_client.emit('create_fact_sheet_api', {
                            'recipient': correlation_id})

        fact_sheet = await create_fact_sheet(geometry, orig_epsg, buffer)

    response = AnalysisResponse.create(
        geo_json, geometry, DEFAULT_EPSG, orig_epsg, buffer, fact_sheet, municipality_number, municipality_name)

    for task in tasks:
        response.result_list.append(task.result())

    analyses_with_map_image = [
        analysis for analysis in response.result_list if analysis.raster_result_map]

    if correlation_id and sio_client:
        sio_client.emit('create_map_images_api', {'recipient': correlation_id})

    map_images = generate_map_images(analyses_with_map_image, fact_sheet)

    container_name = str(uuid4())

    await _upload_images(response, map_images, container_name)

    if correlation_id and sio_client:
        sio_client.emit('create_report_api', {'recipient': correlation_id})

    report = create_pdf(response)

    response.report = await _upload_report(report, container_name)
    
    return response.to_dict()


async def _run_analysis(config_id: UUID, should_analyze: bool, geometry: ogr.Geometry, epsg: int, orig_epsg: int, buffer: int,
                        context: str, include_guidance: bool, include_quality_measurement: bool, sio_client: SimpleClient) -> Analysis:
    config = get_dataset_config(config_id)

    if config is None:
        return None

    if not should_analyze:
        analysis = EmptyAnalysis(
            config.config_id, config, ResultStatus.NOT_RELEVANT)
        await analysis.run()
        return analysis

    start = time.time()
    correlation_id = get_correlation_id()

    analysis = _create_analysis(
        config_id, config, geometry, epsg, orig_epsg, buffer)

    try:
        await analysis.run(context, include_guidance, include_quality_measurement)
    except Exception:
        err = traceback.format_exc()
        _LOGGER.error(err)
        await analysis.set_default_data()
        analysis.result_status = ResultStatus.ERROR

    end = time.time()

    # autopep8: off
    _LOGGER.info(f'Dataset analyzed: {config_id} - {config.name}: {round(end - start, 2)} sec.')
    # autopep8: on

    if correlation_id and sio_client:
        sio_client.emit('dataset_analyzed_api', {
            'dataset': str(config_id), 'recipient': correlation_id})

    return analysis


def _create_analysis(config_id: UUID, config: DatasetConfig, geometry: ogr.Geometry, epsg: int, orig_epsg: int, buffer: int) -> Analysis:
    dataset_type = get_dataset_type(config)

    match dataset_type:
        case 'arcgis':
            return ArcGisAnalysis(config_id, config, geometry, epsg, orig_epsg, buffer)
        case 'ogc_api':
            return OgcApiAnalysis(config_id, config, geometry, epsg, orig_epsg, buffer)
        case 'wfs':
            return WfsAnalysis(config_id, config, geometry, epsg, orig_epsg, buffer)
        case _:
            return None


async def _upload_images(response: AnalysisResponse, map_images: List[Tuple[str, str, bytes | None]], container_name: str) -> None:
    filtered = [map_image for map_image in map_images if map_image[2]]

    if not filtered:
        return

    await create_container(container_name)

    tasks: List[asyncio.Task[str]] = []

    async with asyncio.TaskGroup() as tg:
        for id, name, data in filtered:
            blob_name = f'{kebab_case(name)}.png'
            task = tg.create_task(upload_binary(
                data, container_name, blob_name, 'image/png'), name=id)
            tasks.append(task)

    for task in tasks:
        task_name = task.get_name()
        
        if task_name == 'omraade':
            response.fact_sheet.raster_result_image = task.result()
            continue

        analysis = _find_analysis(response.result_list, task_name)

        if analysis:
            analysis.raster_result_image = task.result()


async def _upload_report(report: bytes, container_name: str) -> str:
    await create_container(container_name)
    pdf_url = await upload_binary(report, container_name, 'rapport.pdf', 'application/pdf')

    return pdf_url


def _find_analysis(analyses: List[Analysis], config_id: str) -> Analysis:
    return next((analysis for analysis in analyses if str(analysis.config_id) == config_id), None)


__all__ = ['run']
