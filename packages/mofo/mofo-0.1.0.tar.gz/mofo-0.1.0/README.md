```python
from mofo import ModelProfiler
import torch
from torchvision.models import resnet18

model = resnet18()
input_size = (1, 3, 224, 224)

profiler = ModelProfiler(model, input_size)

profiler.summary()
profiler.flops_memory(precision='fp16')
profiler.benchmark(precision='fp16', training=True)

```