import logging
import os
from typing import Optional
from optimum.onnxruntime import ORTModelForFeatureExtraction, ORTModelForSequenceClassification
from transformers import AutoConfig

# Configure logging
logger = logging.getLogger(__name__)

class TransformersService: 
    def convert_from_hub(self, model_id: str, output_path: str, task: Optional[str] = None) -> bool:
        """
        Download and convert a model from the Hugging Face Hub.

        Args:
            model_id: The HF model ID (e.g., "sentence-transformers/all-MiniLM-L6-v2").
            output_path: The full path where the .onnx file (and config) will be saved.
            task: (Optional) The specific task (e.g., "feature-extraction", "text-classification").
                  If None, attempts to infer from config.

        Returns:
            True if successful, False otherwise.
        """
        logger.info(f"Starting HF conversion for: {model_id} to {output_path}")
        
        try:
            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # If output_path includes a filename, we mainly need the directory for export
            # Optimum exports as 'model.onnx' by default in the directory.
            # We will handle renaming if a specific filename is requested.
            target_filename = os.path.basename(output_path)
            export_dir = output_dir if output_dir else "."
            
            # Simple auto-task detection logic fallback
            if task is None:
                try:
                    config = AutoConfig.from_pretrained(model_id)
                    arch = config.architectures[0] if config.architectures else ""
                    if "SequenceClassification" in arch:
                        task = "text-classification"
                    else:
                        task = "feature-extraction" # Default safe bet for embeddings
                except Exception:
                    task = "feature-extraction"
            
            logger.info(f"Detected/Using task: {task}")
            
            if task == "feature-extraction":
                model = ORTModelForFeatureExtraction.from_pretrained(model_id, export=True)
            elif task == "text-classification":
                 model = ORTModelForSequenceClassification.from_pretrained(model_id, export=True)
            else:
                # Fallback to feature extraction or raise error
                model = ORTModelForFeatureExtraction.from_pretrained(model_id, export=True)

            # Save model
            model.save_pretrained(export_dir)
            
            # Rename if necessary (Optimum saves as model.onnx)
            default_path = os.path.join(export_dir, "model.onnx")
            if target_filename != "model.onnx" and os.path.exists(default_path):
                final_path = os.path.join(export_dir, target_filename)
                os.replace(default_path, final_path)
                logger.info(f"Renamed model.onnx to {target_filename}")

            logger.info(f"Successfully converted {model_id}")
            return True

        except Exception as e:
            logger.exception(f"HF Conversion failed: {str(e)}")
            return False
