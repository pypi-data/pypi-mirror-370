import torch
from torchinfo import summary
from thop import profile
import time
import pynvml

class ModelProfiler:
    def __init__(self, model: torch.nn.Module, input_size: tuple, device='cuda'):
        self.model = model.to(device)
        self.input_size = input_size
        self.device = device

        # 初始化 NVML 获取 GPU 信息
        if device.startswith('cuda'):
            pynvml.nvmlInit()
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(torch.cuda.current_device())

    def summary(self):
        """打印模型层级结构、参数量、每层 FLOPs（mult_adds）"""
        print(summary(
            self.model,
            input_size=self.input_size,
            col_names=["input_size", "output_size", "num_params", "mult_adds"]
        ))

    def flops_memory(self, precision='fp32'):
        """每层 FLOPs 和参数量统计 + 显存占用估算"""
        dummy_input = torch.randn(self.input_size).to(self.device)
        if precision == 'fp16':
            dummy_input = dummy_input.half()
            self.model.half()
        elif precision == 'bf16':
            dummy_input = dummy_input.to(torch.bfloat16)
            self.model.to(torch.bfloat16)
        else:
            self.model.float()

        flops, params = profile(self.model, inputs=(dummy_input,), verbose=False)

        # 显存占用估算
        param_size = sum(p.numel() for p in self.model.parameters())
        dtype_size = dummy_input.element_size()
        est_memory_mb = (param_size + dummy_input.numel()) * dtype_size / (1024 ** 2)

        # GPU 使用情况
        gpu_mem_info = None
        gpu_util = None
        if self.device.startswith('cuda'):
            info = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
            gpu_mem_info = info.used / (1024 ** 2)
            util = pynvml.nvmlDeviceGetUtilizationRates(self.gpu_handle)
            gpu_util = util.gpu

        print(f"Precision: {precision}")
        print(f"Total FLOPs: {flops / 1e9:.2f} GFLOPs")
        print(f"Total Params: {params / 1e6:.2f} M")
        print(f"Estimated memory usage: {est_memory_mb:.2f} MB")
        if gpu_mem_info:
            print(f"GPU memory used: {gpu_mem_info:.2f} MB, GPU utilization: {gpu_util}%")

    def benchmark(self, precision='fp32', n_runs=50, training=False):
        """
        按 2 的指数倍搜索 batch size，找到吞吐量峰值
        支持训练模式下的吞吐量测量
        显示 GPU 占用率和显存占用率
        """
        batch = self.input_size[0]
        max_batch = batch
        best_throughput = 0
        best_batch = batch
        done = False

        while not done:
            try:
                dummy_input = torch.randn((max_batch, *self.input_size[1:])).to(self.device)
                if precision == 'fp16':
                    dummy_input = dummy_input.half()
                    self.model.half()
                elif precision == 'bf16':
                    dummy_input = dummy_input.to(torch.bfloat16)
                    self.model.to(torch.bfloat16)
                else:
                    self.model.float()

                self.model.train() if training else self.model.eval()

                # 预热
                with torch.set_grad_enabled(training):
                    for _ in range(10):
                        _ = self.model(dummy_input)

                # 测试
                torch.cuda.synchronize()
                start = time.time()
                with torch.set_grad_enabled(training):
                    for _ in range(n_runs):
                        _ = self.model(dummy_input)
                torch.cuda.synchronize()
                throughput = n_runs * max_batch / (time.time() - start)

                # GPU 使用情况
                if self.device.startswith('cuda'):
                    info = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
                    gpu_mem_info = info.used / (1024 ** 2)
                    util = pynvml.nvmlDeviceGetUtilizationRates(self.gpu_handle)
                    gpu_util = util.gpu
                else:
                    gpu_mem_info = gpu_util = None

                print(f"Batch size: {max_batch}, Throughput: {throughput:.2f} samples/sec, "
                      f"GPU memory: {gpu_mem_info:.2f} MB, GPU util: {gpu_util}%")

                # 更新最优吞吐量
                if throughput > best_throughput:
                    best_throughput = throughput
                    best_batch = max_batch
                else:
                    # 吞吐量下降，认为到达峰值
                    done = True

                max_batch *= 2  # 按 2 的指数倍增加 batch size

            except RuntimeError as e:
                if 'out of memory' in str(e):
                    torch.cuda.empty_cache()
                    print(f"Reached OOM at batch size {max_batch}")
                    done = True
                else:
                    raise e

        print(f"Optimal batch size: {best_batch}, max throughput: {best_throughput:.2f} samples/sec")
        return best_batch, best_throughput
