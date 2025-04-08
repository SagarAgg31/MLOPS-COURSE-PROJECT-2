from src.data_processing import DataProcessor
from src.model_training import ModelTraining
from config.path_config import *
from utils.common_functions import read_yaml
from dotenv import find_dotenv, load_dotenv


load_dotenv()

if __name__ == "__main__":

    processor = DataProcessor(input_file=ANIMELIST_CSV, output_dir=PROCESSED_DIR)
    processor.run()

    model_trainer = ModelTraining(data_path=PROCESSED_DIR)
    model_trainer.train_model()