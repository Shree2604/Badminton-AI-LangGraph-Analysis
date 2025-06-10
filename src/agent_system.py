import operator
from typing import Annotated, Sequence, Dict, Any, List

import ray
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from config import RAY_CONFIG
from video_processing import PoseDetector, ShuttlecockTracker
from text_analysis import TextAnalyzer
from strategy_analysis import StrategyAnalyzer

# Initialize Ray if it's not already running
if not ray.is_initialized():
    ray.init(**RAY_CONFIG)

class BadmintonAnalysisState(TypedDict):
    """Represents the state of our badminton analysis graph."""
    video_frames: List[Any]
    commentary: str
    video_analysis: Dict[str, Any]
    text_analysis: str
    strategy_report: str
    final_report: str
    report_path: str

class BadmintonAgentSystem:
    """
    Orchestrates a multi-agent system for badminton analysis using LangGraph.
    Each node in the graph is an agent responsible for a specific task.
    """
    def __init__(self):
        self.agent_graph = self._build_agent_graph()

    def _build_agent_graph(self) -> StateGraph:
        """Builds the LangGraph agent graph with clear, sequential steps."""
        graph = StateGraph(BadmintonAnalysisState)

        graph.add_node("video_agent", self.video_analysis_agent)
        graph.add_node("text_agent", self.text_analysis_agent)
        graph.add_node("strategy_agent", self.strategy_analysis_agent)
        graph.add_node("report_agent", self.report_generation_agent)

        graph.set_entry_point("video_agent")

        graph.add_edge("video_agent", "text_agent")
        graph.add_edge("text_agent", "strategy_agent")
        graph.add_edge("strategy_agent", "report_agent")
        graph.add_edge("report_agent", END)

        return graph.compile()

    def video_analysis_agent(self, state: BadmintonAnalysisState) -> Dict[str, Any]:
        """Agent for analyzing video frames to detect poses and track the shuttlecock."""
        print("--- 🕵️ Video Analysis Agent: Processing... ---")
        # In a real system, you'd process all frames. For this demo, we'll use a sample.
        sample_frame = state["video_frames"][len(state["video_frames"]) // 2]
        
        pose_detector = PoseDetector()
        poses = pose_detector.detect_poses(sample_frame)
        
        # For demonstration, we create a summary string. A real system would store structured data.
        num_poses = len(poses[0].boxes)
        analysis_summary = f"Detected {num_poses} poses in the sample frame."
        print(f"--- ✅ Video Analysis Agent: {analysis_summary} ---")

        return {"video_analysis": {"summary": analysis_summary, "poses": poses}}

    def text_analysis_agent(self, state: BadmintonAnalysisState) -> Dict[str, Any]:
        """Agent for analyzing text commentary."""
        print("--- ✍️ Text Analysis Agent: Processing... ---")
        text_analyzer = TextAnalyzer()
        summary = text_analyzer.analyze_text(state["commentary"], task="summarize")
        print("--- ✅ Text Analysis Agent: Commentary summarized. ---")
        return {"text_analysis": summary}

    def strategy_analysis_agent(self, state: BadmintonAnalysisState) -> Dict[str, Any]:
        """Agent for analyzing game strategy based on video and text data."""
        print("--- 🧠 Strategy Analysis Agent: Processing... ---")
        strategy_analyzer = StrategyAnalyzer()
        report = strategy_analyzer.analyze_strategy(
            video_analysis_results=state["video_analysis"],
            text_analysis_results=state["text_analysis"]
        )
        print("--- ✅ Strategy Analysis Agent: Strategy report generated. ---")
        return {"strategy_report": report}

    def report_generation_agent(self, state: BadmintonAnalysisState) -> Dict[str, Any]:
        """Agent for compiling the final report."""
        print("--- 📄 Report Generation Agent: Compiling final report... ---")
        final_report = f"""
        =========================================
        🏸 BADMINTON ANALYSIS FINAL REPORT 🏸
        =========================================

        🎥 **Video Analysis Summary**:
        {state['video_analysis']['summary']}

        ✍️ **Commentary Summary**:
        {state['text_analysis']}

        🧠 **Strategic Insights**:
        {state['strategy_report']}
        """
        
        # Save the report to the specified file path
        try:
            with open(state["report_path"], "w", encoding="utf-8") as f:
                f.write(final_report)
            print(f'--- ✅ Report saved to {state["report_path"]} ---')
        except IOError as e:
            print(f'--- ❌ Error saving report: {e} ---')

        return {"final_report": final_report}

    def run_analysis(self, video_frames: List[Any], commentary: str, report_path: str):
        """Runs the complete analysis pipeline through the LangGraph."""
        initial_state = {
            "video_frames": video_frames,
            "commentary": commentary,
            "report_path": report_path,
        }
        # The graph is synchronous, but the underlying operations can be async
        final_state = self.agent_graph.invoke(initial_state)
        return final_state

def create_agent_system() -> BadmintonAgentSystem:
    """Factory function to create an instance of the agent system."""
    return BadmintonAgentSystem()

