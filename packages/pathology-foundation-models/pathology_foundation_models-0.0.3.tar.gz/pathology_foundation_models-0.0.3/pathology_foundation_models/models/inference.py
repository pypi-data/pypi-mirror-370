import torch
import torchvision.transforms as T

from PIL.Image import Image
from tqdm import tqdm
from torchvision.datasets import ImageFolder

from pathology_foundation_models.models import FoundationModel
from pathology_foundation_models.models.config import get_inference_fn


def convert_to_batch_tensor(images: Image | list[Image] | torch.Tensor) -> torch.Tensor:
    """
    Converts a single PIL image or a torch tensor of shape (3, H, W) to a batch tensor of shape (1, 3, H, W).

    If the input is already a batch tensor of shape (N, 3, H, W), it will be returned as is.

    :param image: PIL Image or torch.Tensor of shape (3, H, W) or torch Tensor of shape (N, 3, H, W)
    :return: Batch tensor of shape (1, 3, H, W)
    """
    if isinstance(images, list):
        if not all(isinstance(img, Image) for img in images):
            raise TypeError("All items in the list must be PIL Images")
    elif not isinstance(images, Image) and not isinstance(images, torch.Tensor):
        raise TypeError(
            f"Input must be a PIL Image or a torch Tensor, got {type(images)}"
        )

    if isinstance(images, list):
        transform = T.ToTensor()
        image_list = [transform(img) for img in images]
        images = torch.stack(image_list, dim=0)
    if isinstance(images, Image):
        transform = T.ToTensor()
        images = transform(images).unsqueeze(0)  # Add batch dimension
    elif isinstance(images, torch.Tensor):
        if images.dim() == 3:
            images = images.unsqueeze(0)  # Add batch dimension
        elif images.dim() != 4:
            raise ValueError(
                f"Input tensor must be of shape (3, H, W) or (N, 3, H, W). Got {images.shape}"
            )
    else:
        raise TypeError("Input must be a PIL Image or a torch Tensor")

    assert (
        images.dim() == 4
    ), "Unexpected return shape, expected (1, 3, H, W) or (N, 3, H, W)"
    return images


def extract_features(
    images: Image | list[Image] | torch.Tensor, model: FoundationModel
) -> torch.Tensor:
    """
    Extracts features from single PIL image, list of PIL images or tensor using the specified model.

    **Note: images must be of the same size, since inference is performed in a single pass**

    :param image: PIL Image or torch.Tensor of shape (3, H, W) or torch Tensor of shape (N, 3, H, W)
    :param format: either 'pil' or 'torch'
    :param model: FoundationModel instance containing the model and processor
    :return: Extracted features as a torch.Tensor of shape (1, N)
    """
    image_tensor = convert_to_batch_tensor(images)
    image_tensor = image_tensor.to(model.device)

    inference_fn = get_inference_fn(model.model_type)
    features = inference_fn(image_tensor, model.model, model.processor)
    assert features.shape == (
        len(image_tensor),
        model.embedding_dim,
    ), f"Unexpected feature shape {features.shape}, expected ({len(image_tensor)}, {model.embedding_dim}) for model type {model.model_type.value}"
    return features


def extract_features_from_dataset(
    images: ImageFolder,
    model: FoundationModel,
    batch_size: int,
    num_workers: int = 4,
    display_progress: bool = False,
) -> torch.Tensor:
    """
    Extracts features from a collection images using the specified model.
    Performs batching to handle large datasets efficiently.

    **Note: images must be of the same size, since images are batched before each inference pass**

    :param images: ImageFolder dataset containing images
    :param model: FoundationModel instance containing the model and processor
    :param batch_size: Batch size for processing images
    :param num_workers: Number of workers for DataLoader
    :param display_progress: Whether to display a progress bar
    :return: Extracted features as a torch.Tensor of shape (N, D) where
        N is the number of images and D is the embedding dimension
    """
    dataloader = torch.utils.data.DataLoader(
        images, batch_size=batch_size, shuffle=False, num_workers=num_workers
    )
    _embeddings = []
    if display_progress:
        dataloader = tqdm(dataloader, desc="Extracting features")
    for batch, _ in dataloader:  # ignore labels
        embedding_batch = extract_features(batch, model)
        _embeddings.append(embedding_batch)
    return torch.cat(_embeddings, dim=0)
