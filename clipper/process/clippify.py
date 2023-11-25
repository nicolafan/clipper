import json
import logging
from pathlib import Path

import chromadb
from datasets import load_dataset
import torch
from PIL import Image
from tqdm import tqdm
from transformers import CLIPModel, CLIPProcessor

MODEL = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
PROCESSOR = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL.to(DEVICE)


@torch.no_grad()
def clippify_texts(texts: list[str]) -> torch.Tensor:
    """Transforms a list of texts into a tensor of CLIP embeddings.

    Args:
        texts (list[str]): A list of texts.

    Returns:
        torch.Tensor: A tensor of CLIP embeddings.
    """
    inputs = PROCESSOR(text=texts, return_tensors="pt", padding="max_length", truncation=True)
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    outputs = MODEL.get_text_features(**inputs)
    return outputs


@torch.no_grad()
def clippify(images: list[Image.Image]) -> torch.Tensor:
    """Transforms a list of images into a tensor of CLIP embeddings.

    Args:
        images (list[Image.Image]): A list of PIL images.

    Returns:
        torch.Tensor: A tensor of CLIP embeddings.
    """
    inputs = PROCESSOR(images=images, return_tensors="pt", padding=True)
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

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
    # create store
    client = chromadb.PersistentClient(path=str(store_dir))
    image_collection = client.get_or_create_collection(name="clip_image_embeddings")
    text_collection = client.get_or_create_collection(name="clip_text_embeddings2")

    # read metadatas if file is present
    try:
        with open(image_dir / "metadata.json", "r") as f:
            metadatas = json.load(f)
    except FileNotFoundError:
        metadatas = {}

    # get image paths
    image_paths = list(image_dir.glob("*.jpg"))

    logging.info(f"Found {len(image_paths)} images.")
    logging.info("Generating image embeddings...")
    # for i in tqdm(range(0, len(image_paths), batch_size)):
    #     batch_paths = image_paths[i : i + batch_size]
    #     batch = [Image.open(path).convert("RGB") for path in batch_paths]
    #     outputs = clippify(batch)

    #     # add metadatas
    #     batch_metadatas = []
    #     for path in batch_paths:
    #         if path.stem in metadatas:
    #             instance_metadata = metadatas[path.stem]
    #             instance_metadata = {
    #                 k: v for k, v in instance_metadata.items() if v is not None
    #             }
    #             batch_metadatas.append(instance_metadata)
    #         else:
    #             batch_metadatas.append({})

    #     image_collection.add(
    #         embeddings=outputs.tolist(),
    #         ids=[path.stem for path in batch_paths],
    #         metadatas=batch_metadatas,
    #     )
    with open("captions.txt", "r") as f:
        texts = f.readlines()
    logging.info("Generating text embeddings...")
    for i in tqdm(range(0, len(texts), batch_size)):
        batch_texts = texts[i : i + batch_size]
        outputs = clippify_texts(batch_texts)

        text_collection.add(
            embeddings=outputs.tolist(),
            ids=[f"text_{j}" for j in range(i, i + batch_size)],
            metadatas=[{"text": text} for text in batch_texts],
        )


if __name__ == "__main__":
    image_dir = Path("data") / "images"
    store_dir = Path("data") / "store"
    create_embeddings_collection(image_dir, store_dir)