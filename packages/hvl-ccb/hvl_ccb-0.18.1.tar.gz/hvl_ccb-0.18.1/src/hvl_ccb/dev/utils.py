#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
import logging

logger = logging.getLogger(__name__)

msg = (
    "DEPRECATION WARNING:\r\nThe Poller was moved to `hvl_ccb.utils.poller`. Please"
    " adapt your code to import the Poller to:\r\n  from hvl_ccb.utils.poller import"
    " Poller\r\n"
)

logger.error(msg)

from hvl_ccb.utils.poller import Poller  # noqa: F401, E402
