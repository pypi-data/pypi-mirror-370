import torch

def softplus_inverse(tensor: torch.Tensor) -> torch.Tensor:
	"""
	Calculates the necessary tensor such that passing it through softplus yields this tensor
	:param tensor:
	:return:
	"""
	with torch.no_grad():
		return torch.log(torch.e ** tensor - 1)