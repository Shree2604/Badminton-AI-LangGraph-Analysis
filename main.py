import asyncio
import os
from datetime import datetime
from pytube import YouTube
from moviepy.editor import VideoFileClip

from src.agent_system import create_agent_system
from src.data_pipeline import ParallelDataPipeline

# --- Configuration ---
YOUTUBE_URL = "https://www.youtube.com/watch?v=uIj03RsGrJA"  # Tokyo Olympics Gold Medal Match
DATA_DIR = "data"
REPORTS_DIR = "reports"
VIDEO_FILENAME = "downloaded_match.mp4"
CLIP_FILENAME = "match_clip.mp4"
CLIP_DURATION_SECONDS = 120  # 2 minutes

def download_video(url: str, download_dir: str):
    """Downloads a YouTube video to the specified path."""
    try:
        print(f"[STEP 1/6] 📥 Downloading full video from YouTube...")
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        full_video_path = os.path.join(download_dir, VIDEO_FILENAME)
        stream.download(output_path=download_dir, filename=VIDEO_FILENAME)
        print(f"[SUCCESS] ✅ Full video downloaded to {full_video_path}")
        return full_video_path
    except Exception as e:
        print(f"[ERROR] ❌ Could not download video: {e}")
        return None

def extract_clip_from_middle(full_video_path: str, clip_duration: int, output_dir: str) -> str:
    """Extracts a clip of a specified duration from the middle of a video."""
    try:
        print(f"\n[STEP 2/6] ✂️ Extracting a {clip_duration}-second clip from the middle of the video...")
        with VideoFileClip(full_video_path) as video:
            video_duration = video.duration
            if video_duration < clip_duration:
                print(f"[WARNING] ⚠️ Video is shorter than the desired clip duration. Using full video.")
                return full_video_path
            
            start_time = (video_duration / 2) - (clip_duration / 2)
            end_time = start_time + clip_duration
            
            clip = video.subclip(start_time, end_time)
            clip_path = os.path.join(output_dir, CLIP_FILENAME)
            clip.write_videofile(clip_path, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True)
            print(f"[SUCCESS] ✅ Clip extracted and saved to {clip_path}")
            return clip_path
    except Exception as e:
        print(f"[ERROR] ❌ Failed to extract clip: {e}")
        return None

async def main():
    """Main function to run the badminton analysis system."""
    print("\n--- 🏸 Initializing Badminton Analysis System 🏸 ---")

    # 1. Create directories and download video
    os.makedirs(REPORTS_DIR, exist_ok=True)
    full_video_path = download_video(YOUTUBE_URL, DATA_DIR)
    if not full_video_path:
        print("\n--- 🛑 Analysis Aborted: Video download failed. ---")
        return

    # 2. Extract a clip for analysis
    clip_path = extract_clip_from_middle(full_video_path, CLIP_DURATION_SECONDS, DATA_DIR)
    if not clip_path:
        print("\n--- 🛑 Analysis Aborted: Clip extraction failed. ---")
        return

    # 3. Initialize core components
    print("\n[STEP 3/6] 🛠️  Initializing core components (Data Pipeline & Agent System)...")
    data_pipeline = ParallelDataPipeline()
    agent_system = create_agent_system()
    print("[SUCCESS] ✅ Core components initialized.")

    # 4. Process video stream to get frames
    print(f"\n[STEP 4/6] ⚙️  Processing video clip with Dask...")
    video_frames = await data_pipeline.process_video_stream(clip_path)
    if not video_frames:
        print("\n--- 🛑 Analysis Aborted: Could not extract frames from video. ---")
        return
    print(f"[SUCCESS] ✅ Video clip processed into {len(video_frames)} frames.")
    
    # 5. Run the LangGraph agentic workflow
    print("\n[STEP 5/6] 🤖 Starting LangGraph agentic workflow...")
    mock_commentary = ("A fantastic rally between the two players. Player A shows great offense with a series of powerful smashes, "
                       "while Player B defends skillfully. The rally ends with a clever drop shot from Player A.")
    
    # Generate a timestamped report path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORTS_DIR, f"analysis_report_{timestamp}.txt")

    final_state = agent_system.run_analysis(
        video_frames=video_frames, 
        commentary=mock_commentary, 
        report_path=report_path
    )
    print("[SUCCESS] ✅ Agentic workflow complete.")

    # 6. Display the final report
    print("\n[STEP 6/6] 📊 Displaying Final Report...")
    print(final_state.get('final_report', 'No report was generated.'))

    # Shutdown
    data_pipeline.shutdown()
    print("\n--- 🎉 System Shutdown Complete 🎉 ---")

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") == "YOUR_GEMINI_API_KEY":
        print("\n[ERROR] ❌ GEMINI_API_KEY not set in your .env file.")
        print("Please create a .env file and set your Google Gemini API key to run the analysis.")
    else:
        asyncio.run(main())
