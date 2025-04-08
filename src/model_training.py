import comet_ml
import joblib
import pandas as pd
import numpy as np
import os
from tensorflow.keras.callbacks import ModelCheckpoint,LearningRateScheduler,TensorBoard,EarlyStopping
from src.logger import get_logger
from src.custom_exception import CustomException
from config.path_config import *
from src.base_model import BaseModel
import sys
from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)


class ModelTraining:
    def __init__(self,data_path):
        self.data_path = data_path
        self.experiment = comet_ml.Experiment(
            api_key = os.getenv('COMET_API_KEY'),
            project_name='mlops-course-2',
            workspace='sagaragg31'
        )
        logger.info("Model training & COMET-ML intialized...")

    def load_data(self):
        try:
            x_train_array = joblib.load(X_TRAIN_ARRAY)
            x_test_array = joblib.load(X_TEST_ARRAY)
            y_train = joblib.load(Y_TRAIN)
            y_test = joblib.load(Y_TEST)

            logger.info("Data loaded successfully for Model Training")
            return x_train_array,x_test_array,y_train,y_test
        
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise CustomException("Error loading data",sys)
        
    def train_model(self):
        try:
            X_train_array,X_test_array,y_train,y_test = self.load_data()
            n_users = len(joblib.load(USER2USER_ENCODED))
            n_anime = len(joblib.load(ANIME2ANIME_ENCODED))

            base_model = BaseModel(config_path=CONFIG_PATH)
            
            model = base_model.RecommenderNet(n_users=n_users,n_anime=n_anime)

            # To find the best learning rate, we can use the LearningRateScheduler callback
            # Define the learning rate schedule
            start_lr = 0.00001
            min_lr = 0.00001
            max_lr = 0.00005
            batch_size = 10000

            ramum_epochs = 5
            sustain_epochs = 0
            exp_decay  = 0.8

            def lrfn(epoch):
                if epoch < ramum_epochs:
                    return (max_lr-start_lr)/ramum_epochs*epoch + start_lr
                elif epoch < ramum_epochs + sustain_epochs:
                    return max_lr
                else:
                    return (max_lr-min_lr)*exp_decay**(epoch-ramum_epochs-sustain_epochs)+min_lr
                
            lr_callback = LearningRateScheduler(lambda epoch: lrfn(epoch),verbose=0)
        

            model_checkpoint = ModelCheckpoint(
                filepath=CHECKPOINT_FILE_PATH,
                monitor='val_loss',
                save_weights_only=True,
                save_best_only=True,
                mode='min',
                verbose=1
            )

            early_stopping = EarlyStopping(
                patience=3,
                monitor='val_loss',
                mode='min',
                restore_best_weights=True,
            )

            my_callbacks = [model_checkpoint,lr_callback,early_stopping]

            os.makedirs(os.path.dirname(CHECKPOINT_FILE_PATH),exist_ok=True)
            os.makedirs(WEIGHTS_DIR,exist_ok=True)
            os.makedirs(MODEL_DIR,exist_ok=True)

            try:
                history = model.fit(
                        x=X_train_array,  # Pass as a list of two inputs
                        y=y_train,
                        batch_size=batch_size,
                        epochs=20,
                        verbose=1,
                        validation_data=(X_test_array, y_test) , # Validation data must also be in the same format
                        callbacks = my_callbacks
                        )
                model.load_weights(CHECKPOINT_FILE_PATH)
                logger.info("Model training completed successfully")
                for epoch in range(len(history.history['loss'])):
                    train_loss = history.history['loss'][epoch]
                    val_loss = history.history['val_loss'][epoch]

                    self.experiment.log_metric("train_loss", train_loss, step=epoch)
                    self.experiment.log_metric("val_loss", val_loss, step=epoch)

                self.save_model(model)
                #model.save_weights(WEIGHTS_DIR)

            except Exception as e:
                logger.error(f"Error during model training: {e}")
                raise CustomException("Error during model training",sys)
            
        except Exception as e:
            logger.error(f"Error in training model: {e}")
            raise CustomException("Error in training model",sys)
    
    def extract_weights(self,layer_name,model):
        weight_layer = model.get_layer(layer_name)
        weights = weight_layer.get_weights()[0]
        weights = weights/np.linalg.norm(weights,axis=1).reshape((-1,1))
        logger.info(f"Extracted weights from layer {layer_name} successfully")
        logger.info(f"Shape of weights: {weights.shape}")
        return weights

    def save_model(self,model):
        try:
            model.save(MODEL_PATH)
            logger.info("Model saved successfully")

            user_weights = self.extract_weights("user_embedding",model)
            anime_weights = self.extract_weights("anime_embedding",model)

            joblib.dump(user_weights,USER_WEIGHTS_PATH)
            joblib.dump(anime_weights,ANIME_WEIGHTS_PATH)

            self.experiment.log_asset(MODEL_PATH)
            self.experiment.log_asset(ANIME_WEIGHTS_PATH)
            self.experiment.log_asset(USER_WEIGHTS_PATH)

            logger.info("Weights saved successfully")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise CustomException("Error saving model",sys)
        
if __name__ == "__main__":
    model_trainer = ModelTraining(data_path=PROCESSED_DIR)
    model_trainer.train_model()
        
    