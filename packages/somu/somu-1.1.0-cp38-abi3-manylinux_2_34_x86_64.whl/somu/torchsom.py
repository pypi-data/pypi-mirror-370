# The code here is an unoptimized torch version of the true rust
# implementation included for the simplest experiment reproducibility


from typing import Sequence

import numpy
import torch
from tqdm import tqdm

Matrix = Sequence[Sequence[float]]


def generate_grid(dims):
    grid = torch.meshgrid([torch.arange(d) for d in dims])
    return torch.stack([g.flatten() for g in grid], dim=-1)


def compute_distance_matrix(p, q):
    p = p.unsqueeze(1)  # Shape (n_p, 1, d_p)
    return torch.norm(p - q, dim=2)


def sample_rows(arr, n):
    indices = torch.randperm(arr.shape[0])[:n]
    return arr[indices]


def update(batch, influence, centroids):
    dst = compute_distance_matrix(batch, centroids)  # Shape (n_batch, n_centroids)
    bmu = torch.argmin(dst, dim=1)  # Best Matching Units (n_batch,)

    # Obtain the influence BMUs have on other units
    bmu_influence = influence[bmu]  # Shape (n_batch, n_centroids)

    # Compute the update as a convex combination of the batch data points
    differences = batch.unsqueeze(1) - centroids  # Shape (n_batch, n_centroids, dim)
    return (bmu_influence[..., None] * differences).mean(0)


def som(
    data: Matrix,
    units: Sequence | Matrix,
    iters=1,
    sigma_initial=1.0,
    learning_rate=0.5,
    batch_size=1,
    device=None,
    seed=None,
) -> numpy.ndarray:
    """
    Train a Self-Organizing Map (SOM) on the given data.

    Args:
        data (np.ndarray): The input data for training the SOM.
        units (int): The matrix-defined topology of the SOM or dimensions of a regular grid topology.
        iters (int, optional): The number of training iterations (batches). Default is 1.
        sigma_initial (float, optional): The initial neighborhood radius. Default is 1.0.
        learning_rate (float, optional): Step size at each iteration during centroids update. Default is 0.5.
        batch_size (int, optional): The number of samples to process in each batch. Default is 1.
        device (str, optional): The device to use for training ('cpu' or 'cuda'). Default is None.
        seed (int, optional): Random seed for reproducibility. Default is None.

    Returns:
        np.ndarray: The trained SOM weights (centroids)
    """

    torch.set_default_device(device)
    data = torch.tensor(data)
    units = torch.tensor(units)

    if seed:
        torch.manual_seed(seed)

    if len(units.shape) == 1:
        units = generate_grid(units).double()

    m = units.shape[0]
    centroids = sample_rows(data, m)
    unit_dst = compute_distance_matrix(units, units)

    for iter in tqdm(range(iters)):
        sigma = sigma_initial * torch.exp(
            -torch.tensor(iter, dtype=torch.float32) / iters
        )
        influence = torch.exp(-(unit_dst**2) / (2 * sigma**2))
        batch = sample_rows(data, batch_size)
        centroids += learning_rate * update(batch, influence, centroids)

    return centroids.cpu().detach().numpy()
