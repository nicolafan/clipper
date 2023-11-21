from pathlib import Path

import chromadb
import torch
from PIL import Image
from tqdm import tqdm
from transformers import CLIPModel, CLIPProcessor

MODEL = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
PROCESSOR = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


@torch.no_grad()
def clippify(images: list[Image.Image]) -> torch.Tensor:
    """Transforms a list of images into a tensor of CLIP embeddings.

    Args:
        images (list[Image.Image]): A list of PIL images.

    Returns:
        torch.Tensor: A tensor of CLIP embeddings.
    """
    inputs = PROCESSOR(
        images=images,
        return_tensors="pt",
        padding=True,
    )

    outputs = MODEL.get_image_features(inputs["pixel_values"])
    return outputs


def create_embeddings_collection(
    image_dir: Path, store_dir: Path, batch_size: int = 32
):
    """Creates a collection of CLIP embeddings from a directory of images.

    Args:
        image_dir (Path): The directory containing the images.
        store_dir (Path): The directory to store the collection.
        batch_size (int, optional): Batch size for embedding generation. Defaults to 32.
    """
    client = chromadb.PersistentClient(path=str(store_dir))
    collection = client.get_or_create_collection(name="clip_image_embeddings")

    image_paths = list(image_dir.glob("*.jpg"))
    for i in tqdm(range(0, len(image_paths), batch_size)):
        batch_paths = image_paths[i : i + batch_size]
        batch = [Image.open(path) for path in batch_paths]
        outputs = clippify(batch)

        collection.add(
            embeddings=outputs.tolist(), ids=[path.stem for path in batch_paths]
        )


if __name__ == "__main__":
    image_dir = Path("data") / "images"
    store_dir = Path("data") / "store"
    create_embeddings_collection(image_dir, store_dir)
