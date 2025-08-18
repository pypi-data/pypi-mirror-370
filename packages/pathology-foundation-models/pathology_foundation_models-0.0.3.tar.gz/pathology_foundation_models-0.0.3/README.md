# Pathology foundation models

Interface for calling foundation models for histopathology image analysis.

## Installation

To install the package in development mode:

```bash
pip install -e .
```

Or to install with development dependencies:

```bash
pip install -e ".[dev]"
```

For Jupyter notebook support:

```bash
pip install -e ".[notebook]"
```

## Loading models

Models follow a common loading interface: they are all loaded from the `models.load_foundation_model` function. This function takes the following arguments:

* `model_type`: either an enum instance (`models.FoundationModelEnum`) or the corresponding string value for the model type
    - The string representation of an enum value has the same name: so `models.FoundationModelEnum.UNI` and `"UNI"` are equivalent for loading.
* `device` (optional): where to load the model. Defaults to CPU, so be careful if inference should happen on GPU to specify this.
* `token` (optional): HuggingFace API Token, needed for gated models. If not passed, will try to read from `HF_TOKEN` environment variable, and if this variable is not set will prompt you for the token. User access token can be found at [the tokens page on HF settings](https://huggingface.co/settings/tokens)

The return type is a `models.FoundationModel`, a dataclass with the following attributes:

* `model_type`: the enum instance for that model type
* `model_source`: from where that model was installed. For now, only HuggingFace models are supported, so this will be `"hf"`
* `model`: the model itself, a torch `nn.Module`
* `processor`: the pre-processing transform, also a `nn.Module`
* `device` (string): where the weights of that model are loaded

## Running inference

Inference should happen using the `models.extract_features` function, which supports multiple input types. It takes:

* `images`: a single PIL image, a list of PIL images, a single 3d image tensor (`(3, H, W)` ), a 4D image batch tensor (`(N, 3, H, W)`)
* `model`: a `models.FoundationModel` instance

It returns a 2D tensor `(N, D)` with the features for each image, where `N` is the number of images passed and `D` the model's embedding dimension.

You can get the embedding dimension for each model passing the enum instance or type string for your foundation model to the `models.get_embedding_dim` function.

Another type of inference is supported through the `models.extract_features_from_dataset` function, which extract features for all images in a `torchvision.datasets.ImageFolder` dataset in a batched manner. It takes the following parameters:

* `images`: `ImageFolder` dataset
* `model`: `models.FoundationModel` instance
* `batch_size`: number of images per batch
* `num_workers` (optional, defaults to 4): number of workers/threads for loading images in parallel
* `display_progress`: whether to display progress with a tqdm progress bar (see [tqdm](https://github.com/tqdm/tqdm)).

## Creating embedding cache

It is also possible to create an embedding cache (`dataset.EmbeddingCache` class) - which is a torch `TensorDataset` generated from a labeled image dataset (though might work with unlabeled images, but this was not tested).

This dataset can be saved to a file for later use easily using the `.save` method, and created/loaded from file using the `load_from_file` method. Also, being a torch dataset, it can be used in dataloaders and standard pytorch training loops easily.

Example:

```python
from pathology_foundation_models.dataset import EmbeddingCache 
from pathology_foundation_models.models import load_foundation_model

# suppose my_dataset is a torchvision.datasets.ImageFolder

uni = load_foundation_model("UNI", device="cuda", token="hf_MY_TOKEN")
embed_cache = EmbeddingCache.init_from_dataset(
    my_dataset,
    uni,
    batch_size=32,
    num_workers=4,
    display_progress=False,
)  # using init_from_dataset, embeddings will be on same device as model
embed_cache.save("/path/to/my/cache.pt")

copy_cache = EmbeddingCache.load_from_file("/path/to/my/cache.pt", device="cuda")   # all embeddings will be on CUDA
```