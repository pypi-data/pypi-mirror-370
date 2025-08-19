
from viso_sdk.constants.constants import *
from viso_sdk.constants.variables import *
from viso_sdk.constants.modules import *


NODE_TYPE = variables.get_node_type()
NODE_ID = variables.get_node_id()

ROOT_DIR = variables.get_container_dir()
LOG_DIR = variables.get_log_dir()


from pkg_resources import resource_filename
ASSETS_DIR = resource_filename('viso_sdk', 'assets')
FONTS_DIR = resource_filename('viso_sdk', 'assets/fonts')
