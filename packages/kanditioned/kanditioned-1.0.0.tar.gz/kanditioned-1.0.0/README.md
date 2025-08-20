# KANditioned: Fast, Generalizable Training of KANs via Lookup Interpolation

Training is accelerated by orders of magnitude through exploiting the structure of linear (C⁰) spline with uniformly spaced control points, where spline(x) can be calculated as a linear interpolation between the two nearest control points. This is in constrast with the typical summation often seen in B-spline, reducing the amount of computation required and enabling effectively sublinear scaling across the control points dimension.

## Install

```
pip install kanditioned
```

## Usage
```
from kanditioned.kan_layer import KANLayer

layer = KANLayer(in_features=3, out_features=3, init="random_normal", num_control_points=8)

layer.visualize_all_mappings(save_path="kan_mappings.png")
```

It is highly recommended to use this layer with torch.compile, which will provide very significant speedups. Each spline's domain is from 0 to num_control_points - 1. It is also highly recommended to use a normalization layer before each KANLayer

Args:
    in_features (int) – size of each input sample
    out_features (int) – size of each output sample
    init (str) - initialization method:
        "random_normal": Slope of each spline is drawn from a normal distribution and normalized so that each "neuron" has unit "weight" norm.
        "identity": Identity mapping (requires in_features == out_features). At initialization, the layer's output is the same as the inputs.
        "zero": All splines are init zero.
    num_control_points (int): Number of uniformly spaced control points per input feature. Defaults to 32.
    spline_width (float): Width of the spline's domain [-spline_width / 2, spline_width / 2]. Defaults to 4.0.

Methods:
    visualize_all_mappings(save_path=path[optional]) - this will plot out the shape of each spline and its corresponding input and output feature

## How This Works

This implementation of KAN uses a linear (C⁰) spline, with uniformly spaced control points (see Figure 1).

> **Figure 1.** Linear B-spline example:  
> ![Linear B-spline example](image-1.png)

> **Equation 1.** B-spline formula:
>
> <img style="height: 50px" alt="B-spline Formula" src="image.png">

## Roadmap
- Update package with cleaned up, efficient Discrete Cosine Transform and parallel scan (prefix sum) reparameterizations. Both provide isotropic κ ~ O(1) discrete second difference penalty, as opposed to κ ~ O(N^4) for naive B-spline parameterization. This only matters if you care about regularization.
- Proper baselines against MLP and various other KAN implementations on backward and forward passes
    <!-- - https://github.com/ZiyaoLi/fast-kan -->
    <!-- - https://github.com/Blealtan/efficient-kan -->
    <!-- - https://github.com/1ssb/torchkan -->
    <!-- https://github.com/quiqi/relu_kan -->
    <!-- https://github.com/Jerry-Master/KAN-benchmarking -->
    <!-- https://github.com/KindXiaoming/pykan -->
    <!-- https://github.com/mintisan/awesome-kan -->
- Add in feature-major variant
- Add bias, spline range, and normalization parameters
- Add optimized Triton kernel
- Clean up writing

## LICENSE
This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt).