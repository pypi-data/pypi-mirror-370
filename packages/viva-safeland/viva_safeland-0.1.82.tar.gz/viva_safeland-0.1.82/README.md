# ViVa-SAFELAND: A Visual Validation Safe Landing Tool

[![PyPI version](https://badge.fury.io/py/viva_safeland.svg)](https://badge.fury.io/py/viva-safeland)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/viva_safeland.svg)](https://pypi.org/project/viva-safeland)

<div align="center">
  <img
    src="https://github.com/user-attachments/assets/268619ca-97e8-4990-85d5-e6cb7fe26aa0"
    width="1200"
    alt="viva_logo"
    onerror="this.onerror=null; this.src='assets/viva_logo.png';"
    onerror="this.onerror=null; this.src='docs/assets/viva_logo.png';"
  />
</div>

**ViVa-SAFELAND** is an open-source framework for testing and evaluating vision-based navigation strategies for unmanned aerial vehicles, with a special focus on autonomous landing in compliance with safety regulations.

<div align="center">
  <img 
    src="https://github.com/user-attachments/assets/79c7033e-f270-4e69-8924-ef36d655e7d7"
    alt="ViVa-SAFELAND tool" 
    width="1200"
    onerror="this.onerror=null; this.src='assets/viva.png';"
    onerror="this.onerror=null; this.src='docs/assets/viva.png';"
  />
  <figcaption>ViVa-SAFELAND: A Visual Validation Safe Landing Tool</figcaption>
</div>

This documentation contains the official implementation for the paper "[ViVa-SAFELAND: A New Freeware for Safe Validation of Vision-based Navigation in Aerial Vehicles](https://arxiv.org/abs/2503.14719)". It provides a safe, simple, and fair comparison baseline to evaluate and compare different visual navigation solutions under the same conditions.

<div align="center">
  <img 
    src="https://github.com/user-attachments/assets/111961fa-2ef0-4f6b-8c7e-7c54d59ac482" 
    alt="ViVa-SAFELAND Operation" 
    width="1200"
    onerror="this.onerror=null; this.src='assets/viva_operation_optimized_fast.gif';"
    onerror="this.onerror=null; this.src='docs/assets/viva_operation_gif.gif';"
  />
  <figcaption>Example of ViVa-SAFELAND operation</figcaption>
</div>

## Key Features

-   **Real-World Scenarios:** Utilize a collection of high-definition aerial videos from unstructured urban environments, including dynamic obstacles like cars and people.
-   **Emulated Aerial Vehicle (EAV):** Navigate within video scenarios using a virtual moving camera that responds to high-level commands.
-   **Standardized Evaluation:** Provides a safe and fair baseline for comparing different visual navigation solutions under identical, repeatable conditions.
-   **Development & Data Generation:** Facilitates the rapid development of autonomous landing strategies and the creation of custom image datasets for training machine learning models.
-   **Safety-Focused:** Enables rigorous testing and debugging of navigation logic in a simulated environment, eliminating risks to hardware and ensuring compliance with safety regulations.

## Documentation
For detailed usage instructions, examples, and API documentation, please refer to the [ViVa-SAFELAND Documentation](https://juliodltv.github.io/viva_safeland/).

## Citation

If you use ViVa-SAFELAND in your research, please cite the following paper:

```python
@article{soriano2025viva,
  title={ViVa-SAFELAND: a New Freeware for Safe Validation of Vision-based Navigation in Aerial Vehicles},
  author={Miguel S. Soriano-Garcia and Diego A. Mercado-Ravell},
  journal={arXiv preprint arXiv:2503.14719},
  year={2024}
}
```
