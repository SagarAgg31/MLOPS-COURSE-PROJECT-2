from src.custom_exception import CustomException
from src.logger import get_logger
import pandas as pd
import os
import sys
import numpy
from config.path_config import *
from utils.common_functions import read_yaml, load_data
from google.cloud import storage

logger  = get_logger(__name__)

class DataIngestion:
    def __init__(self,config):
        self.config = config['data_ingestion']
        self.bucket_name = self.config['bucket_name']
        self.file_names = self.config['bucket_file_names']

        os.makedirs(RAW_DIR,exist_ok=True)

        logger.info("Data Ingestion initialized.....")

    def download_csv_from_gcp(self):
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            for file_name in self.file_names:
                file_path = os.path.join(RAW_DIR,file_name)

                if file_name =='animelist.csv':
                    blob = bucket.blob(file_name)
                    blob.download_to_filename(file_path)

                    data = pd.read_csv(file_path,nrows=5000000)
                    data.to_csv(file_path, index=False)
                    logger.info("Large file detected only downloading 5M rows")
                else:
                    blob = bucket.blob(file_name)
                    blob.download_to_filename(file_path)
                    logger.info("Downloading smaller files anime and anime_with_synopsis")
        except Exception as e:
            logger.error(f"Error occurred while loading the data from GCP: {e}")
            raise CustomException('Failed to load data from GCP',e)
        
    def run(self):
        try:
            logger.info("Starting data ingestion process...")
            self.download_csv_from_gcp()
            logger.info("Data ingestion completed successfully.")
        except Exception as e:
            logger.error(f"Error occurred during data ingestion: {str(e)}")
            raise CustomException('Failed to run data ingestion',e)
        
if __name__ == "__main__":
    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()

