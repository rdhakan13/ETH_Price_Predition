from src.models.base import Model
import logging

logger = logging.getLogger(__name__)


class ARIMA(Model):
    def __init__(self, params: dict):
        super().__init__(params)
    
    def fit(self, x_train, y_train):
        pass
    
    def predict(self, x_test):
        pass