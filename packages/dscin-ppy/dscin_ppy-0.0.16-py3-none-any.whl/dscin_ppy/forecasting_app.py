
import io
import s3fs
import joblib
import numpy as np
import pandas as pd

from scipy import sparse

import warnings
# Silence future warnings
warnings.simplefilter(action="ignore")

from .aws_utils import build_s3_url
from config.env_config import env_config


class RandomForestPrediction:
    """
    Class to produce predictions on Pieces-Per-Carton and Volume-Per-Piece 
    using pre-trained Random Forest models on historical data.
    
    Load pre-trained models and variables (OneHotEncoder) encoder
    Use enconder to encode input data, to cast it into the shape expected by the prediction models.
    Predict pieces per carton and Volume per Piece for new observations
    
    Predictions are stored in two new column of the input data:
    - "PCs per Carton Pred"
    - "Volume per Piece Pred"

    !!! IMPORTANT !!!
    the input csv file should have all columns used during model training
    otherwise an Exception is raised
    """

    def __init__(self, env_param):
        self.s3_bucket = env_config[env_param]["feature-store-bucket"]
        self.s3_root_key = env_config[env_param]["feature-store-carton-conversion-path"]

    def __call__(self, df):
        # =====================================================================
        # ========================= Data Prepartion ===========================
        log.info("************ DATA PREPARATION ************")

        # Fill missing values
        data = df.fillna("#")

        # Define features for one-hot encoding (all categorical)
        cat_list = [
            "Product Group",
            "Sub Product Group",
            "Type",
            "Country Of Origin",
            "Gender",
            "Division",
            "Season Name",
            "Port of Loading - City name",
            "Vendor",
            "Packing Type",
            "Order Unit"
        ]

        # Assert all required features are in the data
        for feat in cat_list + ["Quantity"]:
            assert feat in data.columns, \
                f"Feature: '{feat}' is missing but necessary for predictions!"

        # =====================================================================
        # =========================== Load Models =============================
        log.info("************ LOAD MODELS ************")

        # Define file names
        s3_key_ppc = self.s3_root_key + "/models/PPC_random_forest_model.pkl"
        s3_key_vpp = self.s3_root_key + "/models/VPP_random_forest_model.pkl"
        s3_key_enc = self.s3_root_key + "/models/encoder.pkl"

        # Open model from S3
        fs = s3fs.S3FileSystem()

        with fs.open(build_s3_url(self.s3_bucket, s3_key_ppc), "rb") as f:
            ppc_model = joblib.load(f)

        with fs.open(build_s3_url(self.s3_bucket, s3_key_vpp), "rb") as f:
            vpp_model = joblib.load(f)

        # Instantiate encoder
        with fs.open(build_s3_url(self.s3_bucket, s3_key_enc), "rb") as f:
            encoder = joblib.load(f)

        # Apply encoding
        data_encoded = encoder.transform(data[cat_list])

        # =====================================================================
        # ========================= Make predictions ==========================
        log.info("************ MAKE PREDICTIONS ************")

        # Add quantity to predictive features
        sparse_qty = sparse.csr_matrix(data["Quantity"]).transpose()
        data_encoded = sparse.hstack([data_encoded, sparse_qty], format="csr")

        # Make predictions for both pieces per carton and Volume per Piece
        ppc_preds = ppc_model.predict(data_encoded)
        vpp_preds = vpp_model.predict(data_encoded)

        # Check that predictions are the same length as the original dataframe
        assert len(ppc_preds) == len(data), \
            "Predictions do not correspond to original data!"

        # Assign predictions back to the data
        data["PCs per Carton Pred"] = ppc_preds
        data["Volume per Piece Pred"] = vpp_preds

        # =====================================================================
        # ================ Check, Correct and Save predictions ================
        log.info("********** CHECK and CORRECT DATA FORMAT **********")

        # Replace "#" with NaN to allow saving in parquet
        data.replace("#", np.nan, inplace=True)

        # Attempt to convert all columns to numeric - skip otherwise
        data = data.apply(pd.to_numeric, errors="ignore")

        # Attempt to convert all columns to datetime
        for col in data.columns:
            if data[col].dtype == "object":
                try:
                    # try converting to datetime
                    data[col] = pd.to_datetime(data[col])
                except ValueError:
                    # skip otherwise
                    pass

        return data