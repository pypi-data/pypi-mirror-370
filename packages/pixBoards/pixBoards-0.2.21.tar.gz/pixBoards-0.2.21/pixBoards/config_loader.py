import os

import yaml

from pixBoards.arguments import args
from pixBoards.log_utils import logger


def load_config(yml_path):
    with open(yml_path, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except:
            logger.warning("does a config.yml exist in this dir? if no then use --makeConfig")


if args.config:
    configFile = args.config
else:
    configFile = "config.yml"
config = load_config(configFile)
config["col_count"] = args.col if args.col else config.get("col_count", [])
config["margin"] = args.margin if args.margin else config.get("margin", [])

masterDir = config["masterDir"]
if args.config:
    masterDir = os.path.join(
        os.path.dirname(masterDir), os.path.splitext(os.path.basename(configFile))[0]
    )

suffix = ""

if args.upload:
    suffix = "_upload"
elif args.imageLists or args.useLists:
    suffix = "_imglist"

outputDir = masterDir + suffix
