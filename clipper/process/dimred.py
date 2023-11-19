from pathlib import Path

import chromadb
import numpy as np
from joblib import dump, load
from sklearn.decomposition import PCA


def train_dimred(models_dir: Path, store_dir: Path):
    client = chromadb.PersistentClient(path=str(store_dir))
    collection = client.get_collection(name="clip_image_embeddings")

    dataset = np.array(
        collection.get(
            include=["embeddings"],
        )["embeddings"]
    )

    model = PCA(n_components=2, random_state=42)
    model.fit(dataset)

    # save model
    dump(model, models_dir / "dimred.joblib")


if __name__ == "__main__":
    models_dir = Path("models")
    store_dir = Path("data") / "store"
    train_dimred(models_dir, store_dir)
