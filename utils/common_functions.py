import os
import pandas as pd
from src.logger import get_logger
from src.custom_exception import CustomException
import yaml
import sys
import pandas as pd

logger = get_logger(__name__)

def read_yaml(file_path:str):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"the file path {file_path} doesn't exist!")
        with open(file_path,'r') as yaml_file:
            config = yaml.safe_load(yaml_file)
            logger.info("The yaml file has been read successfully!")
            return config
    except Exception as e:
        logger.error("Error occurred while reading the yaml file")
        raise CustomException('Failed to read YAML File',e)
    
def load_data(path):
    try:
        logger.info("Loading data")
        return pd.read_csv(path)
    except Exception as e:
        logger.error(f"Error occurred while loading the data {e}")
        raise CustomException('Failed to load data',e)
    
