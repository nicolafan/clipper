from pathlib import Path

import chromadb
import numba
import numpy as np
from joblib import dump, load
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from umap import UMAP


def fit_dimred(models_dir: Path, store_dir: Path):
    """Trains a dimensionality reduction model on the CLIP embeddings.

    Args:
        models_dir (Path): Directory to store the model.
        store_dir (Path): Directory containing the vector store.
    """
    client = chromadb.PersistentClient(path=str(store_dir))

    # prepare image embeddings
    collection = client.get_collection(name="clip_image_embeddings")
    image_embs = np.array(
        collection.get(
            include=["embeddings"],
        )["embeddings"]
    )

    # add a column of 0s to the end of scaled image embeddings
    flags = np.zeros(len(image_embs))
    image_embs = np.column_stack((image_embs, flags))

    # define the custom similarity metric
    @numba.njit
    def custom_cosine(x, y):
        result = 0.0
        norm_x = 0.0
        norm_y = 0.0
        for i in range(x.shape[0] - 1):
            result += x[i] * y[i]
            norm_x += x[i] ** 2
            norm_y += y[i] ** 2

        if x[-1] + y[-1] == 1:
            result *= 2.5
        
        if norm_x == 0.0 and norm_y == 0.0:
            return 0.0
        elif norm_x == 0.0 or norm_y == 0.0:
            return 1.0
        else:
            return 1.0 - (result / np.sqrt(norm_x * norm_y))

    model = UMAP(n_components=2, metric=custom_cosine, disconnection_distance=2)
    model.fit(image_embs)

    dump(model, models_dir / "dimred.joblib")


if __name__ == "__main__":
    models_dir = Path("models")
    store_dir = Path("data") / "store"
    fit_dimred(models_dir, store_dir)
