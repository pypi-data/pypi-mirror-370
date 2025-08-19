"""
    Constant file
"""
import os
from datetime import datetime

_cur_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

year = datetime.now().year

__author__ = "Viso.ai team"
__copyright__ = f"Copyright 2020-{year} viso.ai AG <info@viso.ai>"
__email__ = "g.corrigan@viso.ai"
__license__ = "LGPL3"
__title__ = "viso-sdk-python"

__version__ = "1.1.8"
