"""
Python library for interacting with the SRF's core data platform.

.. note::
    The ``SRFData`` implementation is designed for personal scripting use only.
    If you wish to use API access on behalf of others as part of some
    service, see the ``oauth`` module and contact SRF technical support.

Examples
--------
.. code:: python

    # initialise client for personal scripting use
    from srf_client import SRFData
    srf = SRFData(api_key='...')

    # use a file-based http cache
    from cachecontrol.caches import SeparateBodyFileCache
    srf = SRFData(api_key='...',
                  cache=SeparateBodyFileCache('/var/cache/srf_client'))

    # get last recorded leg
    leg = srf.legs.find_all().last.items[-1]

    # plot ambient pressure for leg
    import pandas as pd
    df = pd.DataFrame(leg.get_data('13'))
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['data'] = pd.to_numeric(df['data'], errors='coerce')
    df.plot('timestamp', 'data')

    # get vehicle and driver id
    vin = di = None
    for measurement in leg.get_data({'VIN', 'DI'}):
        if measurement.type == 'VIN':
            vin = measurement.data
        if measurement.type == 'DI':
            di = measurement.data.split(',')[0]
        if vin and di:
            break

    # list all DAF trucks
    from srf_client import prefix
    page = srf.vehicles.find_all(vin=prefix('XLR'))

    # plot total fuel consumption against total distance for recent trip
    from srf_client import contains
    trip = srf.trips.find_all(types=contains('LFC', 'VDHR')).last.items[0]
    df = trip.get_data_frame(['LFC', 'VDHR'], timedelta(minutes=1))
    df.plot.scatter('VDHR hr total vehicle distance',
                    'LFC engine total fuel used')

"""

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version
__version__ = version(__name__)

from .client import *
from .filter import *
from .model import *
from .sort import *

__all__ = client.__all__ + filter.__all__ + model.__all__ + sort.__all__

try:
    from . import pandas
except ImportError:
    pass

try:
    from .oauth import SRFDataOAuth
except ImportError:
    def SRFDataOAuth(**kwargs):
        """SRF Data client. Requires extra dependencies srf_client[oauth]."""
        raise RuntimeError('Required dependencies not installed')
__all__ += ['SRFDataOAuth']
