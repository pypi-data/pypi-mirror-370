###############################################################################
#
# (C) Copyright 2020 Maikon Araujo
#
# This is an unpublished work containing confidential and proprietary
# information of Maikon Araujo. Disclosure, use, or reproduction
# without authorization of Maikon Araujo is prohibited.
#
###############################################################################

from .quant import *

__doc__ = quant.__doc__
if hasattr(quant, "__all__"):
    __all__ = quant.__all__ + calendars.__all__
