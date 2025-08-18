from typing import Sequence
import numpy

Matrix = Sequence[Sequence[float]]

def som(data: Matrix, units: Sequence | Matrix, iters=1, sigma_initial=1.0, batch_size=1, device=None, seed=None) -> numpy.ndarray:
	"""
	Train a Self-Organizing Map (SOM) on the given data.

	Args:
		data (np.ndarray): The input data for training the SOM.
		units (int): The matrix-defined topology of the SOM or dimensions of a regular grid topology. 
		iters (int, optional): The number of training iterations (batches). Default is 1.
		sigma_initial (float, optional): The initial neighborhood radius. Default is 1.0.
		batch_size (int, optional): The number of samples to process in each batch. Default is 1.
		device (str, optional): The device to use for training ('cpu' or 'cuda'). Default is None.
		seed (int, optional): Random seed for reproducibility. Default is None.

	Returns:
		np.ndarray: The trained SOM weights (centroids)
	"""