"""Module providing __init__ functionality."""

from matrice.utils import dependencies_check

base = [
        "httpx",
        "fastapi",
        "uvicorn",
        "pillow",
        "confluent_kafka[snappy]",
        "aiokafka",
        "filterpy",
        "scipy",
        "scikit-learn",
        "matplotlib",
        "scikit-image",
        "python-snappy",
        "pyyaml",
        "imagehash",
        "opencv-python",
    ]

# Attempt GPU-specific dependencies first. If any of them fail, gracefully fall back to CPU equivalents.
_gpu_deps_ok = (
    dependencies_check(["onnxruntime-gpu"]) and
    dependencies_check(["fast-plate-ocr[onnx-gpu]"])
)
if not _gpu_deps_ok:
    # Fallback to CPU if GPU packages are unavailable or failed to install
    dependencies_check(["onnxruntime"])
    dependencies_check(["fast-plate-ocr[onnx]"])

dependencies_check(base)

if not dependencies_check(["opencv-python"]):
    dependencies_check(["opencv-python-headless"])

from matrice.deploy.server.server import MatriceDeployServer  # noqa: E402
from matrice.deploy.server.server import MatriceDeployServer as MatriceDeploy  # noqa: E402 # Keep this for backwards compatibility
from matrice.deploy.server.inference.inference_interface import InferenceInterface  # noqa: E402
from matrice.deploy.server.proxy.proxy_interface import MatriceProxyInterface  # noqa: E402
from matrice.deploy.client import MatriceDeployClient  # noqa: E402

__all__ = [
    "MatriceDeploy",
    "MatriceDeployServer",
    "InferenceInterface",
    "MatriceProxyInterface",
    "MatriceDeployClient"
]
