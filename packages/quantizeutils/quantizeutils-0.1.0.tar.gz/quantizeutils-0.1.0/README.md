# quantizeutils


Quantization utility modules I used on my [About Quantization](https://github.com/elisa-aleman/ai_python_dev_reference/blob/main/docs/ai_development/About-Quantization.md) guide. 

## Installation

```sh
# @ shell

pip install quantizeutils

# or

poetry add quantizeutils
```

## Usage

### Pre and Post Process FX traced models before QAT

- **`quantizeutils.fx.utils.pre_procecss.propagate_split_share_qparams_pre_process()`**
    - torch.fx.trace() produces weirdly shared quantization parameters when torch.split() is present in the graph. This function fixes that.

- **`quantizeutils.fx.utils.pre_procecss.relu_clamp_backend_config_unshare_observers()`**
    - ReLU and torch.clamp use shared observers in the torch native backend config (default). This expands the quantization min and max unnecessarily keeping, for example, min values below 0 on ReLU nodes and wasting quantization
    scaling space that is not needed. This function fixes that if applied before FX tracing.
- **`quantizeutils.fx.utils.post_process.fuse_qat_bn_post_process()`**
    - Prepares QAT unfused nodes (for example batch normalization) before exporting to ONNX
- **`quantizeutils.fx.utils.post_process.merge_relu_clamp_to_qparams_post_process`**
    - Some modules like Conv+ReLU will fuse automatically in the native backend but remain unfused if exported to ONNX or other backends. This function merges the ReLU and `torch.clamp` node activations to the previous node as part of their q_min and q_max, instead of relying on a secondary node.

### FX Backend for AIEdgeTorch export

[AIEdgeTorch](https://github.com/google-ai-edge/ai-edge-torch) is a powerful (but still volatile) tool to convert torch models to tensorflow through PT2E. Since some models are currently only quantized with FX graphs, I thought to write an FX backend configuration to potentially convert FX models to ai_edge_torch exportable models. More on my [About Quantization](https://github.com/elisa-aleman/ai_python_dev_reference/blob/main/docs/ai_development/About-Quantization.md) guide. 

`quantizeutils.fx.backend_config.ai_edge_backend`