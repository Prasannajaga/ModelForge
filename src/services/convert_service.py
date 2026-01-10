import os
import logging
from typing import Optional, Dict, Union, Tuple
import subprocess
import torch
import re 
from services.wrapper import OnnxExportWrapper
import os
os.environ["TORCH_LOGS"] = "onnx"

# Configure logging
logger = logging.getLogger(__name__)

class ConvertOnnxModel:
    """
    Service to handle conversion of models (PyTorch, TensorFlow, Keras) to ONNX format.
    """
    
    def convert(self, 
                input_path: str, 
                output_path: str, 
                framework: str, 
                input_shapes: Optional[str] = None, 
                opset_version: int = 17, 
                optimize: bool = True) -> bool:
        """
        Convert a model to ONNX.
        
        Args:
            input_path: Path to the source model file.
            output_path: Path where the ONNX model will be saved.
            framework: The source framework ('PyTorch', 'TensorFlow', 'Keras').
            input_shapes: String defining input shapes (e.g., "input_ids:[1,128]").
            opset_version: ONNX Opset version to use.
            optimize: Whether to apply basic optimizations.
            
        Returns:
            True if conversion was successful, False otherwise.
        """
        print(f"Converting model: {input_path}")
        print(f"output path: {output_path}")
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Starting conversion for {framework} model: {input_path}")

        try:
            if "pytorch" in framework.lower():
                return self._convert_pytorch(input_path, output_path, input_shapes, opset_version)
            elif "tensorflow" in framework.lower() or "keras" in framework.lower():
                return self._convert_tensorflow(input_path, output_path, framework, opset_version)
            else:
                logger.error(f"Unsupported framework: {framework}")
                raise ValueError(f"Unsupported framework: {framework}")
                
        except Exception as e:
            logger.exception(f"Conversion failed: {str(e)}")
            raise e


    def is_torchscript_model(model) -> bool: 
        return isinstance(model, torch.jit.RecursiveScriptModule)
    
    def _convert_pytorch(
        self,
        input_path: str,
        output_path: str,
        input_shapes: Optional[str],
        opset: int,
    ) -> bool: 
  
        model = self._load_pytorch_model(input_path)
        model.eval()
  
        dummy_input = self._build_dummy_input(model, input_shapes)
        if not isinstance(dummy_input, tuple):
            dummy_input = (dummy_input,)
  
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True) 

        try:
            if self.is_torchscript_model(model):  
                print("Using legacy path for Script Model")
                # LEGACY PATH (TorchScript → ONNX)  
                torch.onnx.export(
                    model,
                    dummy_input,
                    output_path,
                    opset_version=opset,
                    dynamo=False
                ) 
            else: 
                print("Using modern path")
                torch.onnx.export(
                    model,
                    dummy_input,
                    output_path,
                    opset_version=opset,
                    dynamo=False
                ) 

                # MODERN PATH (Eager → torch.export → ONNX) 
                # exported = torch.export.export(
                #     model,
                #     dummy_input,
                # )

                # # Use file handle to force serialization errors
                # with open(output_path, "wb") as f:
                #     torch.onnx.export(
                #         exported,
                #         f,
                #         opset_version=opset,
                #         input_names=[f"input_{i}" for i in range(len(dummy_input))],
                #         output_names=["output"],
                #     )
  
            if not os.path.isfile(output_path):
                raise RuntimeError(
                    "ONNX export completed but file was not written"
                )

            return True

        except Exception:
            # NEVER swallow exporter errors
            logger.exception("ONNX export failed")
            raise

    def _build_dummy_input(
        self,
        model: torch.nn.Module,
        input_shapes: Optional[str],
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, ...]]:
        """
        Build dummy input tensors for ONNX export.

        input_shapes format examples:
        - "float32[1,3,224,224]"
        - "int64[1,128],int64[1,128]"
        - "[1,10]"  (defaults to float32)
        """

        if input_shapes:
            pattern = r"(?:(?P<dtype>\w+))?\[(?P<shape>[0-9,\s]+)\]"
            matches = list(re.finditer(pattern, input_shapes))

            if not matches:
                raise ValueError(f"Invalid input_shapes format: {input_shapes}")

            tensors = []
            for m in matches:
                dtype_name = m.group("dtype") or "float32"
                if not hasattr(torch, dtype_name):
                    raise ValueError(f"Unsupported dtype: {dtype_name}")

                dtype = getattr(torch, dtype_name)
                shape = [int(x.strip()) for x in m.group("shape").split(",")]

                tensors.append(torch.zeros(*shape, dtype=dtype))

            return tensors[0] if len(tensors) == 1 else tuple(tensors)
 
        # Fallback heuristics (only if user gives nothing) 
        for p in model.parameters():
            if p.ndim == 4:   # CNN-style
                return torch.randn(1, p.shape[1], 224, 224)
            if p.ndim == 2:   # Linear / MLP
                return torch.randn(1, p.shape[1])
 
        return torch.randn(1, 3, 224, 224)

    def _infer_default_input(self, model):
        name = model.__class__.__name__.lower()

        if "resnet" in name or "conv" in name:
            return torch.randn(1, 3, 224, 224)

        raise ValueError(
            "input_shapes is required for this model type"
        )

    def _load_pytorch_model(self, input_path: str) -> torch.nn.Module:
        # 1. TorchScript must be loaded explicitly
        try:
            return torch.jit.load(input_path, map_location="cpu")
        except RuntimeError:
            pass  

        # 2. Try eager model / state-dict
        obj = torch.load(
            input_path,
            map_location="cpu",
            weights_only=False, 
        )

        if isinstance(obj, torch.nn.Module):
            return obj

        if isinstance(obj, dict):
            raise ValueError(
                "State-dict detected. Model architecture is required."
            )

        raise ValueError(f"Unsupported PyTorch model format: {input_path}")


    def _convert_tensorflow(self, input_path: str, output_path: str, framework: str, opset: int) -> bool:
        """
        Handles TensorFlow/Keras conversion using python -m tf2onnx.convert.
        """
        # Using subprocess to avoid conflicting TF/PyTorch imports in the same process if not needed
        cmd = [
            "python", "-m", "tf2onnx.convert",
            "--opset", str(opset),
            "--output", output_path
        ]

        if "keras" in framework.lower() or input_path.endswith('.h5'):
            cmd.extend(["--input", input_path]) # tf2onnx usually takes --input for graphdef or --saved-model or --keras
            # For .h5 keras model:
            # cmd = ["python", "-m", "tf2onnx.convert", "--keras", input_path, "--output", output_path, "--opset", str(opset)]
             
            # Adjusting command for tf2onnx signature
            cmd = [
                "python", "-m", "tf2onnx.convert",
                "--keras", input_path,
                "--output", output_path,
                "--opset", str(opset)
            ]
        else:
             # Assume SavedModel directory or .pb
             cmd.extend(["--saved-model", input_path])

        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"tf2onnx failed: {result.stderr}")
            raise RuntimeError(f"tf2onnx conversion failed: {result.stderr}")
            
        logger.info(f"TensorFlow model successfully converted to {output_path}")
        return True
