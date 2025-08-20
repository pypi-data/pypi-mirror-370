import os
import logging
from argparse import Namespace

import macsylib.config
import macsylib.registries
import macsylib.utils
import macsylib.search_systems
import macsylib.io
from macsylib.system import HitSystemTracker

defaults = macsylib.config.MacsyDefaults()
settings = Namespace(
    db_type='ordered_replicon',
    sequence_db='test.fasta',
    models=['TXSScan', 'all'],  # this model must be installed with msl_data scripts
    worker=4,
    out_dir='my_results'
)
config = macsylib.config.Config(defaults, settings)

os.makedirs(config.working_dir())  # working_dir = out_dir; you have to create this directory

macsylib.init_logger(log_file=os.path.join(config.working_dir(), config.log_file()))
macsylib.logger_set_level(level=logging.INFO)
logger = logging.getLogger('macsylib')
model_registry = macsylib.registries.ModelRegistry()

for model_dir in config.models_dir():
    models_loc_available = macsylib.registries.scan_models_dir(model_dir)
    for model_loc in models_loc_available:
        model_registry.add(model_loc)
models_def_to_detect, models_fam_name, models_version = macsylib.utils.get_def_to_detect(config.models(),
                                                                                         model_registry)

all_systems, rejected_candidates = macsylib.search_systems.search_systems(config, model_registry, models_def_to_detect,
                                                                          logger)
track_multi_systems_hit = HitSystemTracker(all_systems)

with open(os.path.join(config.working_dir(),'all_systems.txt'), "w", encoding='utf8') as tsv_file:
    macsylib.io.systems_to_tsv('TXSScan', '1.1.3',
                               all_systems,
                               track_multi_systems_hit,
                               tsv_file,
                               header=lambda model_name, model_v, skipped_replicons: f'# created by {__file__} script with models {model_name}-{model_v}')
