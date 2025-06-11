"""Utility functions for video frame extraction and pose detection."""
from typing import List, Dict
import cv2
import mediapipe as mp
from tqdm import tqdm
import numpy as np
import os
import os

mp_pose = mp.solutions.pose

def extract_frames(video_path: str, sample_rate: int = 5, target_size: tuple = (640, 360)) -> List[np.ndarray]:
    """Extract and resize frames from video with memory efficiency.
    
    Args:
        video_path: Path to the video file
        sample_rate: Extract every N-th frame
        target_size: Target (width, height) to resize frames
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open {video_path}")
    
    frames = []
    idx = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if idx % sample_rate == 0:
                # Resize frame to reduce memory usage
                if frame.shape[1] != target_size[0] or frame.shape[0] != target_size[1]:
                    frame = cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)
                # Convert BGR to RGB and store
                frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                # Limit number of frames to prevent OOM
                if len(frames) >= 100:  # Max 100 frames
                    break
                    
            idx += 1
            
    except Exception as e:
        print(f"Error processing video: {e}")
        raise
        
    finally:
        cap.release()
        
    if not frames:
        raise RuntimeError(f"No frames extracted from {video_path}")
        
    return frames

def analyze_pose(frames: List[np.ndarray]) -> List[Dict[str, float]]:
    """Analyze pose in each frame and return key metrics."""
    if not frames:
        print("No frames to analyze")
        return []
        
    results = []
    total_frames = len(frames)
    processed_frames = 0
    
    # Simple counter for progress
    def log_progress(current, total):
        progress = (current + 1) / total * 100
        print(f"\rPose analysis: {current + 1}/{total} frames ({progress:.1f}%)", end="", flush=True)
    
    try:
        with mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,  # Reduced complexity for better performance
            enable_segmentation=False,  # Disable segmentation to save memory
            min_detection_confidence=0.3,  # Lower confidence threshold
            min_tracking_confidence=0.3
        ) as pose:
            for i, frame in enumerate(frames):
                try:
                    # Process every 3rd frame to reduce load
                    if i % 3 != 0 and i != len(frames) - 1:  # Always process last frame
                        results.append(None)
                        continue
                        
                    # Convert and process frame
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    res = pose.process(frame_rgb)
                    
                    if res.pose_landmarks:
                        landmarks = res.pose_landmarks.landmark
                        results.append({
                            "confidence": landmarks[mp_pose.PoseLandmark.NOSE].visibility,
                            "nose_x": landmarks[mp_pose.PoseLandmark.NOSE].x,
                            "nose_y": landmarks[mp_pose.PoseLandmark.NOSE].y,
                            # Add more keypoints as needed
                            "left_wrist_x": landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x if landmarks[mp_pose.PoseLandmark.LEFT_WRIST] else 0,
                            "left_wrist_y": landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y if landmarks[mp_pose.PoseLandmark.LEFT_WRIST] else 0,
                            "right_wrist_x": landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x if landmarks[mp_pose.PoseLandmark.RIGHT_WRIST] else 0,
                            "right_wrist_y": landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y if landmarks[mp_pose.PoseLandmark.RIGHT_WRIST] else 0,
                        })
                        processed_frames += 1
                    else:
                        results.append(None)
                        
                    log_progress(i, total_frames)
                        
                except Exception as e:
                    print(f"\nError processing frame {i}: {str(e)}")
                    results.append(None)
                    
    except Exception as e:
        print(f"\nError initializing pose detection: {str(e)}")
        return [{}] * len(frames)
                    
    print(f"\nSuccessfully processed {processed_frames}/{total_frames} frames")
    return results
