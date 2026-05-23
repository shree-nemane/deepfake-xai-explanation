class ChunkGradCAM:
    """
    Wrapper around GradCAM to handle chunk-based processing and temporal alignment.
    """
    def __init__(self, base_gradcam_engine):
        self.base_engine = base_gradcam_engine
        
    def generate_for_chunk(self, input_tensor, target_class=None):
        """
        Generates GradCAM heatmap for a specific 2s chunk.
        """
        # Call the base engine (e.g., the one defined in deepfake_logic.py)
        return self.base_engine.generate(input_tensor, target_class)
