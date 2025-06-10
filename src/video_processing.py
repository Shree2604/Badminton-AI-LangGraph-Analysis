import cv2
import torch
from ultralytics import YOLO
from transformers import DetrImageProcessor, DetrForObjectDetection
from PIL import Image
import numpy as np

class PoseDetector:
    """
    Detects human poses in video frames using a CPU-friendly YOLO model.
    """
    def __init__(self, model_name='yolov8n-pose.pt'):
        """Initializes the pose detector with a YOLO model."""
        self.model = YOLO(model_name)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)
        print(f"PoseDetector using device: {self.device}")

    def detect_poses(self, frame: np.ndarray):
        """
        Detects poses in a single video frame.

        Args:
            frame (np.ndarray): The input video frame in BGR format.

        Returns:
            The results from the YOLO model, containing pose information.
        """
        # YOLO model expects images in RGB format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model(rgb_frame, verbose=False) # verbose=False to reduce console output
        return results

    def draw_poses(self, frame: np.ndarray, results) -> np.ndarray:
        """
        Draws the detected poses onto the frame.

        Args:
            frame (np.ndarray): The original video frame.
            results: The results object from the YOLO model.

        Returns:
            A new frame with the poses drawn on it.
        """
        return results[0].plot() # plot() returns a BGR numpy array with detections

class ShuttlecockTracker:
    """
    Tracks a shuttlecock in video frames using a CPU-friendly DETR model.
    """
    def __init__(self, model_name='facebook/detr-resnet-50'):
        """Initializes the tracker with a DETR model from Hugging Face."""
        self.processor = DetrImageProcessor.from_pretrained(model_name)
        self.model = DetrForObjectDetection.from_pretrained(model_name)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)
        print(f"ShuttlecockTracker using device: {self.device}")

    def track_shuttlecock(self, frame: np.ndarray):
        """
        Detects the shuttlecock in a single video frame.

        Args:
            frame (np.ndarray): The input video frame in BGR format.

        Returns:
            A dictionary with bounding boxes and scores for detected objects.
        """
        # Convert frame to PIL Image
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Preprocess the image
        inputs = self.processor(images=pil_image, return_tensors="pt").to(self.device)

        # Perform inference
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Post-process the results
        target_sizes = torch.tensor([pil_image.size[::-1]])
        results = self.processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.7)[0]

        return results

    def draw_shuttlecock_box(self, frame: np.ndarray, results) -> np.ndarray:
        """
        Draws bounding boxes for the detected shuttlecock.

        Args:
            frame (np.ndarray): The original video frame.
            results (dict): The results from the DETR model.

        Returns:
            A new frame with the shuttlecock bounding box drawn.
        """
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            # The DETR model is trained on COCO, which doesn't have a shuttlecock class.
            # We look for 'sports ball' (label 37) as a proxy.
            if self.model.config.id2label[label.item()] == 'sports ball':
                box = [round(i, 2) for i in box.tolist()]
                x_min, y_min, x_max, y_max = map(int, box)
                
                # Draw rectangle and label
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                cv2.putText(frame, f"Shuttlecock: {score:.2f}", (x_min, y_min - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame
