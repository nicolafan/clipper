import base64
import random
from pathlib import Path

import chromadb
import numpy as np
import torch
from flask import Flask, jsonify
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
SCALER = load(MODELS_DIR / "scaler.joblib")
DIMRED_MODEL = load(MODELS_DIR / "dimred.joblib")


@app.route("/<int:page>")
def get_dataset(page):
    client = chromadb.PersistentClient(path=str(STORE_DIR))
    collection = client.get_collection(name="clip_image_embeddings")

    offset = (page - 1) * 1000

    dataset = collection.get(
        include=["embeddings", "metadatas"], limit=1000, offset=offset
    )
    ids, embs, metadatas = dataset["ids"], dataset["embeddings"], dataset["metadatas"]

    # add a column of 0s to the end of scaled_embs
    flags = np.zeros(len(embs))
    embs = np.column_stack((embs, flags))
    transformed_embs = DIMRED_MODEL.transform(embs)

    # numpy array to list of floats
    transformed_embs = transformed_embs.tolist()
    data = [
        {
            "x": x,
            "y": y,
            "id": id,
            "metadata": metadata,
        }
        for (x, y), id, metadata in zip(transformed_embs, ids, metadatas)
    ]
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
