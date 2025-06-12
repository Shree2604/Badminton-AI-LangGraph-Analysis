"""
Video visualization module for badminton pose analysis.
Creates an MP4 output showing the original video with pose detection overlays.
"""
import cv2
import numpy as np
import os
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import mediapipe as mp
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoVisualizer:
    """Class to visualize pose detection on badminton videos."""
    
    def __init__(self, output_dir: str = "output_videos"):
        """Initialize the video visualizer.
        
        Args:
            output_dir: Directory to save output videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Drawing utilities
        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = mp.solutions.drawing_utils.DrawingSpec(
            thickness=2, circle_radius=2, color=(0, 255, 0)
        )
    
    def process_video(
        self,
        input_path: str,
        output_name: Optional[str] = None,
        sample_rate: int = 5,
        show_progress: bool = True,
        headless: bool = True  # Added headless mode
    ) -> str:
        """Process a video file and create a visualization.
        
        Args:
            input_path: Path to input video file
            output_name: Name for output file (without extension)
            sample_rate: Process every N-th frame (1 = process all frames)
            show_progress: Whether to show progress in console
            
        Returns:
            Path to the output video file
        """
        # Set up input video
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {input_path}")
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Set up output video
        if output_name is None:
            output_name = Path(input_path).stem + "_analysis"
        output_path = self.output_dir / f"{output_name}.mp4"
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            str(output_path),
            fourcc,
            fps / sample_rate,
            (width, height)
        )
        
        try:
            frame_count = 0
            processed_frames = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every N-th frame
                if frame_count % sample_rate == 0:
                    # Convert BGR to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Process frame with MediaPipe
                    results = self.pose.process(rgb_frame)
                    
                    # Draw pose landmarks
                    if results.pose_landmarks:
                        self.mp_drawing.draw_landmarks(
                            image=frame,
                            landmark_list=results.pose_landmarks,
                            connections=self.mp_pose.POSE_CONNECTIONS,
                            landmark_drawing_spec=self.drawing_spec,
                            connection_drawing_spec=self.drawing_spec
                        )
                    
                    # Add frame number and FPS
                    cv2.putText(
                        frame, 
                        f"Frame: {frame_count} | FPS: {fps:.1f}",
                        (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, 
                        (0, 255, 0), 
                        2
                    )
                    
                    # Write frame to output
                    out.write(frame)
                    processed_frames += 1
                    
                    if show_progress and processed_frames % 10 == 0:
                        progress = (frame_count / total_frames) * 100
                        logger.info(f"Processed {processed_frames} frames ({progress:.1f}%)")
                
                frame_count += 1
                
                # Skip window display in headless mode
                if not headless:
                    # Break the loop if 'q' is pressed
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    
        finally:
            # Release resources
            cap.release()
            out.release()
            if not headless:
                cv2.destroyAllWindows()
            
        logger.info(f"Video processing complete. Output saved to: {output_path}")
        return str(output_path)

def analyze_video(
    input_path: str,
    output_dir: Optional[str] = None,
    output_name: Optional[str] = None,
    sample_rate: int = 5,
    show_progress: bool = True
) -> str:
    """Convenience function to analyze a video with pose detection.
    
    Args:
        input_path: Path to input video file
        output_dir: Directory to save output video (default: 'output_videos')
        output_name: Name for output file (without extension)
        sample_rate: Process every N-th frame (1 = process all frames)
        show_progress: Whether to show progress in console
        
    Returns:
        Path to the output video file
    """
    visualizer = VideoVisualizer(output_dir=output_dir or "output_videos")
    return visualizer.process_video(
        input_path=input_path,
        output_name=output_name,
        sample_rate=sample_rate,
        show_progress=show_progress
    )

if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Process a badminton video with pose detection.')
    parser.add_argument('input_video', type=str, help='Path to the input video file')
    parser.add_argument('--output_dir', type=str, default='output_videos', 
                       help='Directory to save output video')
    parser.add_argument('--output_name', type=str, default=None,
                       help='Output file name (without extension)')
    parser.add_argument('--sample_rate', type=int, default=5,
                       help='Process every N-th frame (default: 5)')
    
    args = parser.parse_args()
    
    analyze_video(
        input_path=args.input_video,
        output_dir=args.output_dir,
        output_name=args.output_name,
        sample_rate=args.sample_rate
    )
