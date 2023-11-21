import base64
from pathlib import Path

import chromadb
from flask import Flask, jsonify
from flask_cors import CORS

from ..process.dimred import apply_dimred

app = Flask(__name__)
CORS(app)

PROJECT_DIR = Path.cwd().parents[1]
MODELS_DIR = PROJECT_DIR / "models"
IMAGES_DIR = PROJECT_DIR / "data" / "images"
STORE_DIR = PROJECT_DIR / "data" / "store"


@app.route("/")
def get_dataset():
    dataset = apply_dimred(MODELS_DIR, STORE_DIR)

    client = chromadb.PersistentClient(path=str(STORE_DIR))
    collection = client.get_collection(name="clip_image_embeddings")
    ids = collection.get()["ids"]

    data = {
        "datasets": [
            {
                "label": "CLIP embeddings",
                "fill": False,
                "borderColor": "#f87979",
                "backgroundColor": "#f87979",
                "data": [
                    {
                        "x": x,
                        "y": y,
                        "id": id,
                    }
                    for (x, y), id in zip(dataset, ids)
                ],
                "radius": 5,
                "hoverRadius": 10,
            }
        ]
    }
    return jsonify(data)


@app.route("/get_image/<id>")
def get_image(id):
    filepath = IMAGES_DIR / f"{id}.jpg"
    with open(filepath, "rb") as f:
        image = base64.b64encode(f.read()).decode("utf-8")
    return jsonify({"image": image})
