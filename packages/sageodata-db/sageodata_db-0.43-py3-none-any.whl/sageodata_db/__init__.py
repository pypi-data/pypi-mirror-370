from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

from sageodata_db.utils import *
from sageodata_db.config import *
from sageodata_db.connection import *

import warnings

warnings.filterwarnings("ignore", module="pandas.io.sql", lineno=758)
