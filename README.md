<div align="center">
  <img alt="calotron logo" src="https://raw.githubusercontent.com/mbarbetti/calotron/main/.github/images/calotron-logo.png" width="600"/>
</div>

<h2 align="center">
  <em>Transformer-based models to flash-simulate the LHCb ECAL detector</em>
</h2>

<p align="center">
  <a href="https://www.tensorflow.org/versions"><img alt="TensorFlow versions" src="https://img.shields.io/badge/tensorflow-2.10–2.14-f57000?style=flat"></a>
  <a href="https://www.python.org/downloads"><img alt="Python versions" src="https://img.shields.io/badge/python-3.7–3.11-blue?style=flat"></a>
  <a href="https://pypi.python.org/pypi/calotron"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/calotron"></a>
  <a href="https://github.com/mbarbetti/calotron/blob/main/LICENSE"><img alt="GitHub - License" src="https://img.shields.io/github/license/mbarbetti/calotron"></a>
</p>

<p align="center">
  <a href="https://github.com/mbarbetti/calotron/actions/workflows/tests.yml"><img alt="GitHub - Tests" src="https://github.com/mbarbetti/calotron/actions/workflows/tests.yml/badge.svg?branch=main"></a>
  <a href="https://codecov.io/gh/mbarbetti/calotron"><img alt="Codecov" src="https://codecov.io/gh/mbarbetti/calotron/branch/main/graph/badge.svg?token=DRG8BWC9RR"></a>
</p>

<p align="center">
  <a href="https://github.com/mbarbetti/calotron/actions/workflows/style.yml"><img alt="GitHub - Style" src="https://github.com/mbarbetti/calotron/actions/workflows/style.yml/badge.svg?branch=main"></a>
  <a href="https://github.com/astral-sh/ruff"><img alt="Ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" style="max-width:100%;"></a>
</p>

<!--
[![Docker - Version](https://img.shields.io/docker/v/mbarbetti/calotron?label=docker)](https://hub.docker.com/r/mbarbetti/calotron)
-->

### Transformers

|         Models        | Implementation | Generative ability* | Test | Design inspired by |
|:---------------------:|:--------------:|:-------------------:|:----:|:------------------:|
|     `Transformer`     |       ✅       |          ❌          |  ✅  | [1](https://arxiv.org/abs/1706.03762), [4](https://arxiv.org/abs/2004.08249) |
| `OptionalTransformer` |       ✅       |          ❌          |  ✅  | [1](https://arxiv.org/abs/1706.03762), [4](https://arxiv.org/abs/2004.08249) |
|  `MaskedTransformer`  |       🛠️       |          ❌          |  ❌  | |
|    `GigaGenerator`    |       ✅       |          ✅          |  ✅  | [5](https://arxiv.org/abs/2303.05511), [6](https://arxiv.org/abs/2107.04589) |

*TBA

### Discriminators

|          Models         |  Algorithm  | Implementation | Test | Design inspired by |
|:-----------------------:|:-----------:|:--------------:|:----:|:------------------:|
|     `Discriminator`     |   DeepSets  |       ✅       |  ✅  | [2](https://cds.cern.ch/record/2721094), [3](https://arxiv.org/abs/1703.06114) |
| `PairwiseDiscriminator` |   DeepSets  |       ✅       |  ✅  | [2](https://cds.cern.ch/record/2721094), [3](https://arxiv.org/abs/1703.06114) |
|    `GNNDiscriminator`   |     GNN     |       🛠️       |  ❌  | |
|   `GigaDiscriminator`   | Transformer |       ✅       |  ✅  | [5](https://arxiv.org/abs/2303.05511), [6](https://arxiv.org/abs/2107.04589), [7](https://arxiv.org/abs/2006.04710) |

### References
1. A. Vaswani _et al._, "Attention Is All You Need", [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
2. N.M. Hartman, M. Kagan and R. Teixeira De Lima, "Deep Sets for Flavor Tagging on the ATLAS Experiment", [ATL-PHYS-PROC-2020-043](https://cds.cern.ch/record/2721094)
3. M. Zaheer _et al._, "Deep Sets", [arXiv:1703.06114](https://arxiv.org/abs/1703.06114)
4. L. Liu _et al._, "Understanding the Difficulty of Training Transformers", [arXiv:2004.08249](https://arxiv.org/abs/2004.08249)
5. M. Kang _et al._, "Scaling up GANs for Text-to-Image Synthesis", [arXiv:2303.05511](https://arxiv.org/abs/2303.05511)
6. K. Lee _et al._, "ViTGAN: Training GANs with Vision Transformers", [arXiv:2107.04589](https://arxiv.org/abs/2107.04589)
7. H. Kim, G. Papamakarios and A. Mnih, "The Lipschitz Constant of Self-Attention", [arXiv:2006.04710](https://arxiv.org/abs/2006.04710)

### Credits
Transformer implementation freely inspired by the TensorFlow tutorial [Neural machine translation with a Transformer and Keras](https://www.tensorflow.org/text/tutorials/transformer) and the Keras tutorial [Image classification with Vision Transformer](https://keras.io/examples/vision/image_classification_with_vision_transformer).
