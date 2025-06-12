"""LangGraph agentic pipeline orchestrating video, audio and report generation with parallel processing."""
from langgraph.graph import StateGraph
from typing import Dict, List, Any, TypedDict, Optional, Callable
import asyncio
import numpy as np
from typing_extensions import TypedDict as TypedDictExt
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing
import psutil
import logging
from functools import partial
from pathlib import Path

from .video_utils import VideoProcessor
from .audio_utils import extract_audio, transcribe
from .report_generator import generate_report
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

try:
    from langgraph.utils import add_function_nodes  # type: ignore
except ImportError:  # fallback for older/newer langgraph
    def add_function_nodes(graph, node_funcs):  # type: ignore
        """Simple replacement: add each function as a node by name."""
        for name, fn in node_funcs.items():
            graph.add_node(name, fn)

class BadmintonState(TypedDict):
    video_path: str
    frames: list
    pose: list
    transcript: str
    report: str
    errors: List[Dict[str, str]]

def get_optimal_workers() -> int:
    """Calculate optimal number of worker processes based on system resources."""
    try:
        cpu_count = multiprocessing.cpu_count()
        mem_gb = psutil.virtual_memory().available / (1024 ** 3)  # Convert to GB
        # Use minimum of CPU cores or 1 worker per 2GB of available RAM
        workers = min(cpu_count, max(2, int(mem_gb // 2)))
        logger.info(f"Optimal workers calculated: {workers} (CPU: {cpu_count}, RAM: {mem_gb:.1f}GB)")
        return workers
    except Exception as e:
        logger.warning(f"Error calculating optimal workers, defaulting to 4: {str(e)}")
        return 4

async def process_video_frames(video_path: str, sample_rate: int = 5) -> List[Dict]:
    """Process video frames using the VideoProcessor."""
    try:
        processor = VideoProcessor(target_size=(854, 480))
        results = []
        
        # Process video in batches
        for result in processor.process_video(
            video_path,
            sample_rate=sample_rate,
            batch_size=16,
            max_workers=multiprocessing.cpu_count()
        ):
            results.append(result)
            
        return results
    except Exception as e:
        logger.error(f"Error processing video frames: {str(e)}")
        raise

def build_pipeline(api_key: str):
    graph = StateGraph(BadmintonState)
    
    # Initialize state with errors list
    def init_state(state: BadmintonState) -> dict:
        return {"errors": []}

    # Node 1: Extract frames
    async def fn_extract_frames(state: BadmintonState) -> dict:
        """Extract video frames with progress tracking."""
        logger.info("[STEP] Extracting frames from video...")
        try:
            frames = await asyncio.to_thread(
                extract_frames, 
                state["video_path"], 
                sample_rate=5
            )
            return {"frames": frames, "errors": state.get("errors", [])}
        except Exception as e:
            error_msg = f"Frame extraction failed: {str(e)}"
            logger.error(error_msg)
            return {"errors": [{"step": "extract_frames", "error": error_msg}]}

    # Node 2: Process Video Frames
    async def fn_process_video(state: Dict[str, Any]) -> dict:
        """Process video frames using the optimized VideoProcessor."""
        if not state.get("video_path"):
            error_msg = "No video path provided"
            logger.error(error_msg)
            return {"errors": state.get("errors", []) + [{"step": "process_video", "error": error_msg}]}

        logger.info("[STEP] Processing video frames...")
        try:
            # Process frames in parallel using VideoProcessor
            pose_results = await process_video_frames(
                state["video_path"],
                sample_rate=3  # Process every 3rd frame by default
            )
            
            # Extract and format results
            if not pose_results:
                raise ValueError("No pose detection results returned")
                
            return {
                "frames": [r["keypoints"] for r in pose_results if r],
                "pose_metrics": [r.get("metrics", {}) for r in pose_results if r],
                "timestamps": [r["timestamp"] for r in pose_results if r],
                "errors": state.get("errors", [])
            }
            
        except Exception as e:
            error_msg = f"Video processing failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "errors": state.get("errors", []) + [{"step": "process_video", "error": error_msg}]
            }

    # Node 3: Audio Processing
    async def fn_audio_processing(state: Dict[str, Any]) -> dict:
        """Extract and process audio from video."""
        if not state.get("video_path"):
            error_msg = "No video path provided for audio extraction"
            logger.error(error_msg)
            return {"errors": state.get("errors", []) + [{"step": "audio_processing", "error": error_msg}]}

        logger.info("[STEP] Processing audio...")
        try:
            # Extract audio
            audio_path = await asyncio.to_thread(
                extract_audio,
                state["video_path"]
            )
            
            # Transcribe audio
            transcript = await asyncio.to_thread(
                transcribe,
                audio_path
            )
            
            return {"transcript": transcript, "errors": state.get("errors", [])}
            
        except Exception as e:
            error_msg = f"Audio processing failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "transcript": "",
                "errors": state.get("errors", []) + [{"step": "audio_processing", "error": error_msg}]
            }

    # Node 4: Report Generation
    async def fn_generate_report(state: Dict[str, Any]) -> dict:
        """Generate final analysis report."""
        if not state.get("frames") and not state.get("transcript"):
            error_msg = "No analysis results available for report generation"
            logger.error(error_msg)
            return {"errors": state.get("errors", []) + [{"step": "report_generation", "error": error_msg}]}

        logger.info("[STEP] Generating report...")
        try:
            # Generate report using the report generator
            report = await asyncio.to_thread(
                generate_report,
                pose_metrics=state.get("pose_metrics", []),
                transcription=state.get("transcript", ""),
                role="coach",  # Default role, can be customized
                player_num=1,    # Default player number, can be customized
                locale="en"      # Default locale, can be customized
            )
            
            return {
                "report": report,
                "errors": state.get("errors", [])
            }
            
        except Exception as e:
            error_msg = f"Report generation failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "report": "",
                "errors": state.get("errors", []) + [{"step": "report_generation", "error": error_msg}]
            }

    # Node 4: Report Generation
    async def fn_generate_report(state: Dict[str, Any]) -> dict:
        """Generate final report with error handling."""
        logger.info("[STEP] Generating final report...")
        try:
            # Initialize Gemini with the API key if not already done
            from badminton_ai.report_generator import init_gemini
            init_gemini(api_key)
            
            report = await asyncio.to_thread(
                generate_report,
                pose_metrics=state.get("pose_metrics", []),
                transcription=state.get("transcript", ""),
                role="coach",  # Default role, can be customized based on state if needed
                player_num=1,    # Default player number
                locale="en"      # Default locale
            )
            return {"report": report, "errors": state.get("errors", [])}
        except Exception as e:
            error_msg = f"Report generation failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"errors": state.get("errors", []) + [{"step": "report_generation", "error": error_msg}]}

    # Add nodes to graph with proper error handling
    graph.add_node("process_video_node", fn_process_video)
    graph.add_node("audio_processing_node", fn_audio_processing)
    graph.add_node("report_generation_node", fn_generate_report)

    # Define edges with error handling
    graph.set_entry_point("process_video_node")
    graph.add_edge("process_video_node", "audio_processing_node")
    graph.add_edge("audio_processing_node", "report_generation_node")
    graph.set_finish_point("report_generation_node")
    
    # Add error handling edges
    graph.add_edge("process_video_node", "report_generation_node")
    graph.add_edge("audio_processing_node", "report_generation_node")

    return graph.compile()


async def run_analysis(
    video_path: str, 
    api_key: str,
    callback: Optional[Callable] = None,
    sample_rate: int = 3,
    target_size: tuple = (854, 480)
) -> Dict[str, Any]:
    """
    Run the analysis pipeline with enhanced error handling and progress updates.
    
    Args:
        video_path: Path to the input video file
        api_key: API key for external services
        callback: Optional callback function for progress updates
        sample_rate: Process every N-th frame (default: 3)
        target_size: Target frame size as (width, height)
        
    Returns:
        Dictionary containing analysis results and metadata
    """
    logger.info(f"Starting analysis for video: {video_path}")
    start_time = datetime.now()
    
    # Initialize state
    initial_state = {
        "video_path": video_path,
        "api_key": api_key,
        "sample_rate": sample_rate,
        "target_size": target_size,
        "frames": [],
        "pose_metrics": [],
        "timestamps": [],
        "transcript": "",
        "report": "",
        "errors": [],
        "metadata": {
            "start_time": start_time.isoformat(),
            "video_path": video_path,
            "sample_rate": sample_rate,
            "target_size": target_size
        }
    }
    
    # Build and run pipeline
    try:
        pipeline = build_pipeline(api_key)
        
        # Define progress callback wrapper
        async def progress_callback(current: str, total: int, **kwargs):
            if callback:
                await callback(current, total, **kwargs)
                
        # Update progress
        await progress_callback("Starting analysis...", 0)
        
        # Run the pipeline
        if hasattr(pipeline, 'ainvoke'):
            result = await pipeline.ainvoke(initial_state)
        else:
            # Fallback to sync invocation in a thread
            def sync_invoke():
                nonlocal result
                result = pipeline.invoke(initial_state)
                update_progress("pipeline_complete", 0.9)
                return result
            
            result = await asyncio.to_thread(sync_invoke)
        
        # Process results
        if not result:
            raise ValueError("Pipeline execution returned no results")
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare final result
        result = {
            "analysis": result,
            "metadata": {
                "success": True,
                "execution_time_seconds": execution_time,
                "frames_processed": len(initial_state.get("frames", [])),
                "timestamp": datetime.now().isoformat(),
                "sample_rate": sample_rate,
                "target_size": target_size
            }
        }
        
        update_progress("analysis_complete", 1.0)
        
        return result
        
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        logger.exception(error_msg)
        
        # Return error state
        execution_time = (datetime.now() - start_time).total_seconds()
        return {
            "errors": [{"step": "pipeline_execution", "error": error_msg}],
            "metadata": {
                "success": False,
                "error": error_msg,
                "execution_time_seconds": execution_time,
                "timestamp": datetime.now().isoformat()
            }
        }
