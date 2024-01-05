import base64
import random
from pathlib import Path

import chromadb
import numpy as np
import torch
from flask import Flask, jsonify, request
from flask_cors import CORS
from joblib import load
from transformers import CLIPModel, CLIPProcessor

app = Flask(__name__)
CORS(app)

PROJECT_DIR = Path.cwd().parents[1]
MODELS_DIR = PROJECT_DIR / "models"
IMAGES_DIR = PROJECT_DIR / "data" / "images"
STORE_DIR = PROJECT_DIR / "data" / "store"
CLIP_PROCESSOR = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
CLIP_MODEL = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
DIMRED_MODEL = load(MODELS_DIR / "dimred.joblib")


@app.route("/<int:page>")
def get_dataset(page):
    client = chromadb.PersistentClient(path=str(STORE_DIR))
    collection = client.get_collection(name="clip_image_embeddings")

    all_ids = collection.get(include=[])["ids"]
    random.seed(42)
    random.shuffle(all_ids)

    offset = (page - 1) * 1000
    ids_to_get = all_ids[offset : offset + 1000]

    dataset = collection.get(
        ids=ids_to_get, include=["embeddings", "metadatas"]
    )
    ids, embs, metadatas = dataset["ids"], dataset["embeddings"], dataset["metadatas"]

    # add a column of 0s to the end of scaled_embs
    flags = np.zeros(len(embs))
    embs = np.column_stack((embs, flags))
    transformed_embs = DIMRED_MODEL.transform(embs)

    # numpy array to list of floats
    transformed_embs = transformed_embs.tolist()
    data = {
        "dataset": [
            {
                "x": x,
                "y": y,
                "id": id,
                "metadata": metadata,
            }
            for (x, y), id, metadata in zip(transformed_embs, ids, metadatas)
        ],
        "nPages": np.ceil(collection.count() / 1000),
    }
    return jsonify(data)


@app.route("/get_image/<id>")
def get_image(id):
    filepath = IMAGES_DIR / f"{id}.jpg"
    with open(filepath, "rb") as f:
        image = base64.b64encode(f.read()).decode("utf-8")
    return jsonify({"image": image})


@app.route("/query/<query>")
def make_query(query):
    with torch.no_grad():
        input = CLIP_PROCESSOR(
            text=[query],
            images=None,
            return_tensors="pt",
            padding=True,
        )
        output = CLIP_MODEL.get_text_features(**input)

    # add a column of 1s to the end of scaled_output
    flags = np.ones(len(output))
    output = np.column_stack((output, flags))
    transformed_output = DIMRED_MODEL.transform(output)

    transformed_output = transformed_output.tolist()
    data = [
        {
            "x": x,
            "y": y,
            "text": query,
        }
        for x, y in transformed_output
    ]
    return jsonify(data)


@app.route("/search")
def search():
    client = chromadb.PersistentClient(path=str(STORE_DIR))
    collection = client.get_collection(name="clip_image_embeddings")

    # read get param query
    query = request.args.get("query")

    with torch.no_grad():
        input = CLIP_PROCESSOR(
            text=[query],
            images=None,
            return_tensors="pt",
            padding=True,
        )
        output = CLIP_MODEL.get_text_features(**input)

    results = collection.query(query_embeddings=output.tolist()[0], n_results=100)
    results["images"] = [[]]

    # load images
    for id in results["ids"][0]:
        filepath = IMAGES_DIR / f"{id}.jpg"
        with open(filepath, "rb") as f:
            image = base64.b64encode(f.read()).decode("utf-8")
        results["images"][0].append(image)

    return jsonify(results)
