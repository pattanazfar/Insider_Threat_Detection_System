import os
import joblib
from core.interfaces import ModelArtifactWriter


class JoblibModelWriter(ModelArtifactWriter):

    def save(self, obj, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(obj, path)