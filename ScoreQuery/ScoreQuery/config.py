from gsuid_core.utils.plugins_config.models import (
    GSC,
    GsStrConfig,
    GsBoolConfig,
    GsListStrConfig,
)

CONIFG_DEFAULT = {
    'testconfig': GsListStrConfig('testconfig', '没用到', ['testconfig']),
}

from gsuid_core.data_store import get_res_path

CONFIG_PATH = get_res_path() / 'ScoreQuery' / 'config.json'

import os

os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

from gsuid_core.utils.plugins_config.gs_config import StringConfig

seconfig = StringConfig('ScoreQuery', CONFIG_PATH, CONIFG_DEFAULT)
