"""
Optimized video processing module with parallel pose detection.

Features:
- Batch processing for better CPU/GPU utilization
- Memory-efficient frame handling
- Parallel processing with ThreadPoolExecutor
- Adaptive frame sampling
- Caching for repeated operations
"""
import cv2
import numpy as np
import mediapipe as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Generator, Tuple
import time
from dataclasses import dataclass
from functools import lru_cache
import os

# Constants
DEFAULT_BATCH_SIZE = 16
FRAME_CACHE_SIZE = 100  # Number of frames to keep in memory

@dataclass
class FrameBatch:
    """Batch of frames for processing"""
    frames: List[np.ndarray]
    frame_numbers: List[int]
    timestamps: List[float]

class VideoProcessor:
    def __init__(self, target_size: Tuple[int, int] = (640, 360), use_gpu: bool = False):
        """
        Initialize the video processor.
        
        Args:
            target_size: Target frame size as (width, height)
            use_gpu: Whether to enable GPU acceleration if available
        """
        self.target_size = target_size
        self.use_gpu = use_gpu
        self.pose = self._init_pose_model()
        self.frame_cache = {}
        
    def _init_pose_model(self):
        """Initialize MediaPipe pose model with optimized settings"""
        return mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def process_video(
        self,
        video_path: str,
        sample_rate: int = 5,
        batch_size: int = DEFAULT_BATCH_SIZE,
        max_workers: int = None
    ) -> Generator[Dict, None, None]:
        """
        Process video with optimized pipeline
        
        Args:
            video_path: Path to video file
            sample_rate: Process every N-th frame
            batch_size: Number of frames to process in parallel
            max_workers: Maximum number of worker threads
            
        Yields:
            Dictionary with frame analysis results
        """
        if max_workers is None:
            max_workers = min(32, (os.cpu_count() or 1) + 4)
            
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Process video in batches
            for batch in self._batch_frames(video_path, sample_rate, batch_size):
                # Submit batch for processing
                future_to_frame = {
                    executor.submit(
                        self._process_single_frame,
                        frame,
                        frame_num,
                        timestamp
                    ): frame_num
                    for frame, frame_num, timestamp in zip(
                        batch.frames, batch.frame_numbers, batch.timestamps
                    )
                }
                
                # Process completed tasks
                for future in as_completed(future_to_frame):
                    frame_num = future_to_frame[future]
                    try:
                        result = future.result()
                        if result:
                            yield result
                    except Exception as e:
                        print(f"Error processing frame {frame_num}: {str(e)}")
                            
                # Clear processed frames from memory
                del batch.frames[:]
                
    def _batch_frames(
        self,
        video_path: str,
        sample_rate: int,
        batch_size: int
    ) -> Generator[FrameBatch, None, None]:
        """Generate batches of frames from video"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video file: {video_path}")

        try:
            batch = FrameBatch([], [], [])
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    if batch.frames:  # Yield remaining frames
                        yield batch
                    break
                        
                if frame_count % sample_rate == 0:
                    # Preprocess frame
                    processed_frame = self._preprocess_frame(frame)
                    
                    # Add to batch
                    batch.frames.append(processed_frame)
                    batch.frame_numbers.append(frame_count)
                    batch.timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
                    
                    # Yield batch when full
                    if len(batch.frames) >= batch_size:
                        yield batch
                        batch = FrameBatch([], [], [])
                            
                frame_count += 1
                
                # Memory management
                if len(self.frame_cache) > FRAME_CACHE_SIZE:
                    self.frame_cache.clear()
                        
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame"""
        # Convert to RGB and resize
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return cv2.resize(
            frame_rgb,
            self.target_size,
            interpolation=cv2.INTER_AREA
        )

    def _process_single_frame(
        self,
        frame: np.ndarray,
        frame_number: int,
        timestamp: float
    ) -> Optional[Dict]:
        """Process a single frame with pose detection"""
        try:
            # Convert to BGR for MediaPipe
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Process with MediaPipe
            results = self.pose.process(frame_bgr)
            
            if not results.pose_landmarks:
                return None
                
            # Extract key landmarks
            landmarks = results.pose_landmarks.landmark
            keypoints = {
                "nose": self._get_landmark(landmarks, mp.solutions.pose.PoseLandmark.NOSE),
                "left_wrist": self._get_landmark(landmarks, mp.solutions.pose.PoseLandmark.LEFT_WRIST),
                "right_wrist": self._get_landmark(landmarks, mp.solutions.pose.PoseLandmark.RIGHT_WRIST),
                "left_elbow": self._get_landmark(landmarks, mp.solutions.pose.PoseLandmark.LEFT_ELBOW),
                "right_elbow": self._get_landmark(landmarks, mp.solutions.pose.PoseLandmark.RIGHT_ELBOW),
                "left_shoulder": self._get_landmark(landmarks, mp.solutions.pose.PoseLandmark.LEFT_SHOULDER),
                "right_shoulder": self._get_landmark(landmarks, mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER),
            }
            
            # Calculate metrics
            metrics = self._calculate_metrics(keypoints)
            
            return {
                "frame_number": frame_number,
                "timestamp": timestamp,
                "keypoints": keypoints,
                "metrics": metrics
            }
            
        except Exception as e:
            print(f"Error in frame {frame_number}: {str(e)}")
            return None

    def _get_landmark(self, landmarks, landmark_type) -> Dict[str, float]:
        """Helper to get landmark coordinates"""
        lm = landmarks[landmark_type]
        return {
            "x": lm.x,
            "y": lm.y,
            "z": lm.z if hasattr(lm, 'z') else 0,
            "visibility": lm.visibility
        }

    def _calculate_metrics(self, keypoints: Dict) -> Dict:
        """Calculate performance metrics from keypoints"""
        metrics = {}
        
        # Calculate distance between wrists
        if all(k in keypoints for k in ["left_wrist", "right_wrist"]):
            lw = keypoints["left_wrist"]
            rw = keypoints["right_wrist"]
            metrics["wrist_distance"] = np.sqrt(
                (lw["x"] - rw["x"])**2 + 
                (lw["y"] - rw["y"])**2
            )
            
        # Calculate elbow angles
        for side in ["left", "right"]:
            shoulder = keypoints.get(f"{side}_shoulder")
            elbow = keypoints.get(f"{side}_elbow")
            wrist = keypoints.get(f"{side}_wrist")
            
            if all([shoulder, elbow, wrist]):
                # Calculate angle at elbow
                angle = self._calculate_angle(
                    (shoulder["x"], shoulder["y"], 0),
                    (elbow["x"], elbow["y"], 0),
                    (wrist["x"], wrist["y"], 0)
                )
                metrics[f"{side}_elbow_angle"] = angle
                
        return metrics
    
    def _calculate_angle(self, a: Tuple[float, float, float], 
                        b: Tuple[float, float, float], 
                        c: Tuple[float, float, float]) -> float:
        """Calculate the angle between three points"""
        ba = np.array(a) - np.array(b)
        bc = np.array(c) - np.array(b)
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        return np.degrees(angle)

    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'pose'):
            self.pose.close()

# Helper function for backward compatibility
def extract_frames(video_path: str, sample_rate: int = 5, target_size: tuple = (640, 360)) -> List[np.ndarray]:
    """Legacy function for backward compatibility"""
    processor = VideoProcessor(target_size=target_size)
    frames = []
    for result in processor.process_video(video_path, sample_rate=sample_rate):
        frames.append(result['keypoints'])
    return frames

def analyze_pose(frames: List[np.ndarray]) -> List[Dict[str, float]]:
    """Legacy function for backward compatibility"""
    # This is a simplified version that works with the new processor
    processor = VideoProcessor()
    results = []
    for i, frame in enumerate(frames):
        # Convert frame to the format expected by the processor
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        result = processor._process_single_frame(frame_bgr, i, i/30.0)  # 30 FPS assumption
        results.append(result or {})
    return results
