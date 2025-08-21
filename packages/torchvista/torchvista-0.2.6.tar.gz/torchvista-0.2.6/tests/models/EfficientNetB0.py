import torch
from torchvista import trace_model
from torchvision import models

model = models.efficientnet_b0(weights=None)
example_input = torch.randn(1, 3, 224, 224)
trace_model(model, example_input, forced_module_tracing_depth=7)


forced_module_tracing_depth = 7

code_contents = """\
import torch
from torchvista import trace_model
from torchvision import models

model = models.efficientnet_b0(weights=None)
example_input = torch.randn(1, 3, 224, 224)
trace_model(model, example_input, forced_module_tracing_depth=7)

"""