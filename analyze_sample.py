#!/usr/bin/env python3
"""
Script to analyze a sample badminton video with pose detection visualization.
"""
import os
import sys
from pathlib import Path
from badminton_ai.video_visualizer import VideoVisualizer

def main():
    # Get the directory of the current script
    script_dir = Path(__file__).parent
    
    # Path to the sample video (assuming it's in the same directory as this script)
    sample_video = script_dir / "sample2.mp4"
    
    # Check if sample video exists
    if not sample_video.exists():
        print(f"Error: Sample video not found at {sample_video}")
        print("Please place a video named 'sample2.mp4' in the same directory as this script.")
        return
    
    # Create output directory if it doesn't exist
    output_dir = script_dir / "output_videos"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting analysis of {sample_video.name}")
    print("This may take a few minutes depending on video length...")
    
    try:
        # Initialize the visualizer
        visualizer = VideoVisualizer(output_dir=str(output_dir))
        
        # Process the video with pose detection
        output_path = visualizer.process_video(
            input_path=str(sample_video),
            output_name="sample_analysis",
            sample_rate=2,  # Process every 2nd frame for better visualization
            show_progress=True,
            headless=True  # Run in headless mode
        )
        
        print(f"\n✅ Analysis complete!")
        print(f"📹 Output video saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ An error occurred during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
