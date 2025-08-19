import importlib
import itertools
import json
import logging
import sys

import pytest
from moto import mock_dynamodb
from nzshm_common.location.coded_location import CodedLocation
from nzshm_common.location.location import LOCATIONS_BY_ID

from toshi_hazard_store import model
from toshi_hazard_store.model import openquake_models
from toshi_hazard_store.model.revision_4 import hazard_models  # noqa we need this for adaptation

log = logging.getLogger(__name__)


# ref https://docs.pytest.org/en/7.3.x/example/parametrize.html#deferring-the-setup-of-parametrized-resources
def pytest_generate_tests(metafunc):
    if "adapted_rlz_model" in metafunc.fixturenames:
        metafunc.parametrize("adapted_rlz_model", ["pynamodb"], indirect=True)
    if "adapted_hazagg_model" in metafunc.fixturenames:
        metafunc.parametrize("adapted_hazagg_model", ["pynamodb"], indirect=True)
    if "adapted_meta_model" in metafunc.fixturenames:
        metafunc.parametrize("adapted_meta_model", ["pynamodb"], indirect=True)


@pytest.fixture
def adapted_hazagg_model(request, tmp_path):
    if request.param == 'pynamodb':
        with mock_dynamodb():
            openquake_models.HazardAggregation.create_table(wait=True)
            yield openquake_models
            openquake_models.HazardAggregation.delete_table()
    else:
        raise ValueError("invalid internal test config")


@pytest.fixture
def adapted_rlz_model(request, tmp_path):

    importlib.reload(sys.modules['toshi_hazard_store.model.openquake_models'])

    log.debug(f"adapted_rlz_model() called with {request.param}")
    if request.param == 'pynamodb':
        log.debug(f"mock_dynamodb {request.param}")
        with mock_dynamodb():
            openquake_models.OpenquakeRealization.create_table(wait=True)
            yield openquake_models
            openquake_models.OpenquakeRealization.delete_table()
    else:
        raise ValueError("invalid internal test config")


@pytest.fixture
def adapted_meta_model(request, tmp_path):

    if request.param == 'pynamodb':
        with mock_dynamodb():
            # set_adapter(Model)
            openquake_models.ToshiOpenquakeMeta.create_table(wait=True)
            yield openquake_models
            openquake_models.ToshiOpenquakeMeta.delete_table()
    else:
        raise ValueError("invalid internal test config")


@pytest.fixture()
def get_one_meta():
    yield lambda cls=openquake_models.ToshiOpenquakeMeta: cls(
        partition_key="ToshiOpenquakeMeta",
        hazard_solution_id="AMCDEF",
        general_task_id="GBBSGG",
        hazsol_vs30_rk="AMCDEF:350",
        # updated=dt.datetime.now(tzutc()),
        # known at configuration
        vs30=350,  # vs30 value
        imts=['PGA', 'SA(0.5)'],  # list of IMTs
        locations_id='AKL',  # Location code or list ID
        source_tags=["hiktlck", "b0.979", "C3.9", "s0.78"],
        source_ids=["SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEwODA3NQ==", "RmlsZToxMDY1MjU="],
        inv_time=1.0,
        # extracted from the OQ HDF5
        src_lt=json.dumps(dict(sources=[1, 2])),  # sources meta as DataFrame JSON
        gsim_lt=json.dumps(dict(gsims=[1, 2])),  # gmpe meta as DataFrame JSON
        rlz_lt=json.dumps(dict(rlzs=[1, 2])),  # realization meta as DataFrame JSON
    )


@pytest.fixture(scope='function')
def get_one_rlz():
    imtvs = []
    for t in ['PGA', 'SA(0.5)', 'SA(1.0)']:
        levels = range(1, 51)
        values = range(101, 151)
        imtvs.append(model.IMTValuesAttribute(imt="PGA", lvls=levels, vals=values))

    location = CodedLocation(lat=-41.3, lon=174.78, resolution=0.001)
    yield lambda cls=openquake_models.OpenquakeRealization: cls(
        values=imtvs,
        rlz=10,
        vs30=450,
        hazard_solution_id="AMCDEF",
        source_tags=["hiktlck", "b0.979", "C3.9", "s0.78"],
        source_ids=["SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEwODA3NQ==", "RmlsZToxMDY1MjU="],
    ).set_location(location)


@pytest.fixture(scope='function')
def get_one_hazagg():
    lvps = list(map(lambda x: model.LevelValuePairAttribute(lvl=x / 1e3, val=(x / 1e6)), range(1, 51)))
    location = CodedLocation(lat=-41.3, lon=174.78, resolution=0.001)
    yield lambda: openquake_models.HazardAggregation(
        values=lvps, agg=model.AggregationEnum.MEAN.value, imt="PGA", vs30=450, hazard_model_id="HAZ_MODEL_ONE"
    ).set_location(location)


@pytest.fixture
def many_rlz_args():
    yield dict(
        TOSHI_ID='FAk3T0sHi1D==',
        vs30s=[250, 500, 1000, 1500],
        imts=['PGA'],
        locs=[CodedLocation(o['latitude'], o['longitude'], 0.001) for o in list(LOCATIONS_BY_ID.values())[:2]],
        rlzs=[x for x in range(5)],
    )


@pytest.fixture(scope='function')
def build_rlzs_v3_models(many_rlz_args, adapted_rlz_model):
    """New realization handles all the IMT levels."""

    n_lvls = 29

    def model_generator():
        # rlzs = [x for x in range(5)]
        for rlz in many_rlz_args['rlzs']:
            values = []
            for imt, val in enumerate(many_rlz_args['imts']):
                values.append(
                    model.IMTValuesAttribute(
                        imt=val,
                        lvls=[x / 1e3 for x in range(1, n_lvls)],
                        vals=[x / 1e6 for x in range(1, n_lvls)],
                    )
                )
            for loc, vs30 in itertools.product(many_rlz_args["locs"][:5], many_rlz_args["vs30s"]):
                yield model.OpenquakeRealization(
                    values=values,
                    rlz=rlz,
                    vs30=vs30,
                    site_vs30=vs30,
                    hazard_solution_id=many_rlz_args["TOSHI_ID"],
                    source_tags=['TagOne'],
                    source_ids=['Z', 'XX'],
                ).set_location(loc)

    yield model_generator


@pytest.fixture
def many_hazagg_args():
    yield dict(
        HAZARD_MODEL_ID='MODEL_THE_FIRST',
        vs30s=[250, 350, 500, 1000, 1500],
        imts=['PGA', 'SA(0.5)'],
        aggs=[model.AggregationEnum.MEAN.value, model.AggregationEnum._10.value],
        locs=[CodedLocation(o['latitude'], o['longitude'], 0.001) for o in list(LOCATIONS_BY_ID.values())],
    )


@pytest.fixture(scope='function')
def build_hazard_aggregation_models(many_hazagg_args, adapted_hazagg_model):
    def model_generator():
        n_lvls = 29
        lvps = list(map(lambda x: model.LevelValuePairAttribute(lvl=x / 1e3, val=(x / 1e6)), range(1, n_lvls)))
        for loc, vs30, agg in itertools.product(
            many_hazagg_args['locs'][:5], many_hazagg_args['vs30s'], many_hazagg_args['aggs']
        ):
            for imt, val in enumerate(many_hazagg_args['imts']):
                yield model.HazardAggregation(
                    values=lvps,
                    vs30=vs30,
                    agg=agg,
                    imt=val,
                    hazard_model_id=many_hazagg_args['HAZARD_MODEL_ID'],
                ).set_location(loc)

    yield model_generator


@pytest.fixture()
def build_hazagg_models(adapted_hazagg_model, build_hazard_aggregation_models):
    with adapted_hazagg_model.HazardAggregation.batch_write() as batch:
        for item in build_hazard_aggregation_models():
            batch.save(item)
