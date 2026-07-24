import logging
from core.db_repository import DBRepository
from model.db_adapter import FinalFeaturesReader
from model.file_adapter import JoblibModelWriter
from model.train_pipeline import run_training_pipeline

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    repo = DBRepository()

    # ✅ Inject DB function (Loose Coupling)
    reader = FinalFeaturesReader(repo.get_final_features)

    # ✅ Writers
    model_writer = JoblibModelWriter()
    scaler_writer = JoblibModelWriter()

    try:
        run_training_pipeline(
            reader,
            model_writer,
            scaler_writer
        )

        print("\n✅ Isolation Forest trained using DB data\n")

    except Exception as e:
        print(f"❌ Error: {e}")