import logging
from typing import Type

from . import location_indexed_model, openquake_models, revision_4
from .attributes import IMTValuesAttribute, LevelValuePairAttribute
from .constraints import AggregationEnum, IntensityMeasureTypeEnum, ProbabilityEnum, VS30Enum
from .disagg_models import DisaggAggregationExceedance, DisaggAggregationOccurence
from .disagg_models import drop_tables as drop_disagg
from .disagg_models import migrate as migrate_disagg
from .gridded_hazard import GriddedHazard
from .gridded_hazard import drop_tables as drop_gridded
from .gridded_hazard import migrate as migrate_gridded
from .location_indexed_model import LocationIndexedModel
from .openquake_models import VS30_KEYLEN, HazardAggregation, OpenquakeRealization, ToshiOpenquakeMeta
from .openquake_models import drop_tables as drop_openquake
from .openquake_models import migrate as migrate_openquake
from .openquake_models import vs30_nloc001_gt_rlz_index
from .revision_4 import (
    CompatibleHazardCalculation,
    HazardAggregateCurve,
    HazardCurveProducerConfig,
    HazardRealizationCurve,
)
from .revision_4 import drop_tables as drop_r4
from .revision_4 import migrate as migrate_r4

log = logging.getLogger(__name__)


def migrate():
    """Create the tables, unless they exist already."""
    migrate_openquake()
    migrate_gridded()
    migrate_disagg()


def drop_tables():
    """Drop em"""
    drop_openquake()
    drop_gridded()
    drop_disagg()
