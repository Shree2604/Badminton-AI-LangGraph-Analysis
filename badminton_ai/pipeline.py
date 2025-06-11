"""LangGraph agentic pipeline orchestrating video, audio and report generation."""
from langgraph.graph import StateGraph
from typing import Dict, List, Any, TypedDict
import asyncio
from typing_extensions import TypedDict as TypedDictExt

from .video_utils import extract_frames, analyze_pose
from .audio_utils import extract_audio, transcribe
from .report_generator import generate_report

try:
    from langgraph.utils import add_function_nodes  # type: ignore
except ImportError:  # fallback for older/newer langgraph
    def add_function_nodes(graph, node_funcs):  # type: ignore
        """Simple replacement: add each function as a node by name."""
        for name, fn in node_funcs.items():
            graph.add_node(name, fn)


from typing_extensions import TypedDict

class BadmintonState(TypedDict):
    video_path: str
    frames: list
    pose: list
    transcript: str
    report: str

def build_pipeline(api_key: str):
    graph = StateGraph(BadmintonState)

    # Node 1: Extract frames
    async def fn_extract_frames(state: BadmintonState) -> dict:
        """Extract video frames."""
        print("[STEP] Extracting frames from video ...")
        frames = await asyncio.to_thread(extract_frames, state["video_path"], sample_rate=5)
        return {"frames": frames}

    # Node 2: Pose analysis
    async def fn_pose(state: Dict[str, Any]):
        print("[STEP] Running pose analysis ...")
        pose_metrics = await asyncio.to_thread(analyze_pose, state["frames"])
        return {"pose": pose_metrics}

    # Node 3: Audio + transcript
    async def fn_audio(state: BadmintonState) -> dict:
        """Extract and transcribe audio."""
        print("[STEP] Extracting & transcribing audio ...")
        audio_path = await asyncio.to_thread(extract_audio, state["video_path"])
        text = await asyncio.to_thread(transcribe, audio_path)
        return {"transcript": text}

    # Node 4: Report
    async def fn_report(state: Dict[str, Any]):
        print("[STEP] Generating coaching report with Gemini ...")
        report = await asyncio.to_thread(generate_report, state["pose"], state["transcript"])
        return {"report": report}

    # Add nodes with unique names
    graph.add_node("extract_frames_node", fn_extract_frames)
    graph.add_node("pose_analysis_node", fn_pose)
    graph.add_node("audio_processing_node", fn_audio)
    graph.add_node("report_generation_node", fn_report)
    
    # Set up the graph flow
    graph.set_entry_point("extract_frames_node")
    graph.add_edge("extract_frames_node", "pose_analysis_node")
    graph.add_edge("extract_frames_node", "audio_processing_node")
    graph.add_edge("pose_analysis_node", "report_generation_node")
    graph.add_edge("audio_processing_node", "report_generation_node")
    graph.set_finish_point("report_generation_node")

    return graph.compile()


async def run_analysis(video_path: str, api_key: str) -> str:
    pipeline = build_pipeline(api_key)
    
    # Prepare initial state
    initial_state = {
        "video_path": video_path,
        "frames": [],
        "pose": [],
        "transcript": "",
        "report": ""
    }
    
    # Run the pipeline
    if hasattr(pipeline, "ainvoke"):
        result = await pipeline.ainvoke(initial_state)
    else:
        result = await asyncio.to_thread(pipeline.invoke, initial_state)
    
    return result["report"]
