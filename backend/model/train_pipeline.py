import logging
from core.interfaces import DataReader, ModelArtifactWriter
from model.train_anomaly import train_isolation_forest
from config.settings import ANOMALY_MODEL_PATH, SCALER_PATH

logger = logging.getLogger(__name__)


def run_training_pipeline(
    reader: DataReader,
    model_writer: ModelArtifactWriter,
    scaler_writer: ModelArtifactWriter
):
    logger.info("🚀 Training Pipeline Started")

    df = reader.read()

    model, scaler = train_isolation_forest(df)

    model_writer.save(model, ANOMALY_MODEL_PATH)
    scaler_writer.save(scaler, SCALER_PATH)

    logger.info("✅ Model & Scaler Saved Successfully")

    return model


# ===============================
# ENTRY POINT (VERY IMPORTANT 🔥)
# ===============================
if __name__ == "__main__":
    import logging
    from core.db_repository import DBRepository
    from model.db_adapter import FinalFeaturesReader
    from model.file_adapter import JoblibModelWriter

    # ✅ ENABLE LOGGING
    logging.basicConfig(level=logging.INFO)

    logger.info("Starting Training Script...")

    repo = DBRepository()

    # ✅ Reader (DB → features)
    reader = FinalFeaturesReader(repo.get_final_features)

    # ✅ Writers (save model + scaler)
    model_writer = JoblibModelWriter()
    scaler_writer = JoblibModelWriter()

    try:
        run_training_pipeline(
            reader,
            model_writer,
            scaler_writer
        )

        print("\n✅ Training Completed Successfully\n")

    except Exception as e:
        print(f"❌ Error: {e}")