import torch
from torchvision import models

model = models.squeezenet1_0(weights=None)
example_input = torch.randn(1, 3, 224, 224)

forced_module_tracing_depth = 4
collapse_modules_after_depth = 2

code_contents = """
import torch
from torchvista import trace_model
from torchvision import models

model = models.squeezenet1_0(weights=None)
example_input = torch.randn(1, 3, 224, 224)
trace_model(model, example_input, forced_module_tracing_depth=4, collapse_modules_after_depth=2)

"""