"""[ DESCRIPTION ]: Interface for the Kaya Python Module SDK V2.0."""

# flake8: noqa
# EXCEPTIONS

from kaya_module_sdk.src.exceptions.files_not_found import FilesNotFoundException
from kaya_module_sdk.src.exceptions.kconstraint import KayaConstraintException
from kaya_module_sdk.src.exceptions.kit_failure import KITFailureException
from kaya_module_sdk.src.exceptions.kmetadata import KayaMetadataException
from kaya_module_sdk.src.exceptions.kunimplemented import KayaUnimplementedException
from kaya_module_sdk.src.exceptions.kvl_failure import KVLFailureException
from kaya_module_sdk.src.exceptions.malformed_results import MalformedResultsException
from kaya_module_sdk.src.exceptions.module_not_found import ModuleNotFoundException
from kaya_module_sdk.src.exceptions.tests_not_found import TestsNotFoundException
from kaya_module_sdk.src.exceptions.web_server_down import WebServerDownException
from kaya_module_sdk.src.exceptions.write_failure import WriteFailureException
from kaya_module_sdk.src.module.arguments import Args
from kaya_module_sdk.src.module.config import KConfig
from kaya_module_sdk.src.module.returns import Rets
from kaya_module_sdk.src.module.template import Module
from kaya_module_sdk.src.testing.ktest import setup_kit_framework
from kaya_module_sdk.src.testing.kvl_harness import KVL
from kaya_module_sdk.src.utils.constraints.equal import keq
from kaya_module_sdk.src.utils.constraints.greater import kgt
from kaya_module_sdk.src.utils.constraints.greater_or_equal import kgte
from kaya_module_sdk.src.utils.constraints.length import klen
from kaya_module_sdk.src.utils.constraints.less import klt
from kaya_module_sdk.src.utils.constraints.less_or_equal import klte
from kaya_module_sdk.src.utils.constraints.max_len import kmaxlen
from kaya_module_sdk.src.utils.constraints.maximum import kmax
from kaya_module_sdk.src.utils.constraints.min_len import kminlen
from kaya_module_sdk.src.utils.constraints.minimum import kmin
from kaya_module_sdk.src.utils.constraints.value_range import krange
from kaya_module_sdk.src.utils.logger import (
    setup_datadog_logging,
    setup_logging,
    DatadogJSONFormatter,
)
from kaya_module_sdk.src.utils.metadata.display_description import (
    DisplayDescription,
    load_markdown,
)
from kaya_module_sdk.src.utils.generators.methods import kaya_io
from kaya_module_sdk.src.utils.metadata.display_name import DisplayName
from kaya_module_sdk.src.utils.metadata.equal import EQ
from kaya_module_sdk.src.utils.metadata.greater import GT
from kaya_module_sdk.src.utils.metadata.greater_or_equal import GTE
from kaya_module_sdk.src.utils.metadata.less import LT
from kaya_module_sdk.src.utils.metadata.less_or_equal import LTE
from kaya_module_sdk.src.utils.metadata.max_len import MaxLen
from kaya_module_sdk.src.utils.metadata.maximum import Max
from kaya_module_sdk.src.utils.metadata.min_len import MinLen
from kaya_module_sdk.src.utils.metadata.minimum import Min
from kaya_module_sdk.src.utils.metadata.eq_len import EQLen
from kaya_module_sdk.src.utils.metadata.const import Const
from kaya_module_sdk.src.utils.metadata.not_const import NotConst
from kaya_module_sdk.src.utils.metadata.order import Order
from kaya_module_sdk.src.utils.metadata.value_range import ValueRange
from kaya_module_sdk.src.utils.metadata.variadic import Variadic
from kaya_module_sdk.src.utils.metadata.prediction import Prediction
from kaya_module_sdk.src.utils.shell import shell_cmd
from kaya_module_sdk.src.utils.check import is_matrix
from kaya_module_sdk.src.datatypes.classifier import KClassifier
