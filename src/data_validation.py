import os
import json
import logging
import pandas as pd
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataValidation:
    def __init__(self, artifacts_dir: str = "artifacts"):
        self.artifacts_dir = artifacts_dir
        os.makedirs(self.artifacts_dir, exist_ok=True)
        self.report_path = os.path.join(self.artifacts_dir, "validation_report.json")
        
    def validate(self, df_products: pd.DataFrame, df_interactions: pd.DataFrame) -> Dict[str, Any]:
        """Validates products and interactions dataframes and generates a report."""
        logger.info("Validating dataset schemas and values...")
        
        report: Dict[str, Any] = {
            "products": {},
            "interactions": {},
            "status": "SUCCESS"
        }
        
        # 1. Validate Products
        product_cols = ["product_id", "product_name", "category", "description"]
        missing_product_cols = [col for col in product_cols if col not in df_products.columns]
        report["products"]["missing_columns"] = missing_product_cols
        report["products"]["row_count"] = len(df_products)
        report["products"]["null_values"] = df_products.isnull().sum().to_dict()
        report["products"]["duplicates"] = int(df_products.duplicated(subset=["product_id"]).sum())
        
        # 2. Validate Interactions
        interaction_cols = ["user_id", "product_id", "rating", "purchased", "views", "clicks"]
        missing_interaction_cols = [col for col in interaction_cols if col not in df_interactions.columns]
        report["interactions"]["missing_columns"] = missing_interaction_cols
        report["interactions"]["row_count"] = len(df_interactions)
        report["interactions"]["null_values"] = df_interactions.isnull().sum().to_dict()
        report["interactions"]["duplicates"] = int(df_interactions.duplicated(subset=["user_id", "product_id"]).sum())
        
        # Rating boundaries validation
        if "rating" in df_interactions.columns:
            invalid_ratings = df_interactions[(df_interactions["rating"] < 1.0) | (df_interactions["rating"] > 5.0)]
            report["interactions"]["invalid_ratings_count"] = len(invalid_ratings)
        else:
            report["interactions"]["invalid_ratings_count"] = 0

        # General status
        if missing_product_cols or missing_interaction_cols:
            report["status"] = "FAILED"
            logger.error(f"Schema validation failed. Missing cols in products: {missing_product_cols}, interactions: {missing_interaction_cols}")
        else:
            logger.info("Data validation completed successfully.")
            
        # Write report
        with open(self.report_path, "w") as f:
            json.dump(report, f, indent=4)
        logger.info(f"Validation report saved to {self.report_path}")
        
        return report

if __name__ == "__main__":
    from data_ingestion import DataIngestion
    ingestor = DataIngestion()
    prod, inter = ingestor.load_data()
    validator = DataValidation()
    val_report = validator.validate(prod, inter)
    print("Validation Report Status:", val_report["status"])
