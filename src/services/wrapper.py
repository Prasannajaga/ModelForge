import torch

class OnnxExportWrapper(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, *args, **kwargs):
        out = self.model(*args, **kwargs)

        if isinstance(out, dict):
            # deterministic ordering
            return tuple(out[k] for k in sorted(out.keys()))

        return out
