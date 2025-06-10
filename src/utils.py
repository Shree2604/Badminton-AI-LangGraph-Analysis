import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

@dataclass
class ProcessingTask:
    task_id: str
    task_type: str
    data: Any
    priority: int = 0
    timestamp: float = time.time()

class TaskType(Enum):
    VIDEO_ANALYSIS = "video_analysis"
    TEXT_ANALYSIS = "text_analysis"
    POSE_DETECTION = "pose_detection"
    SHUTTLECOCK_TRACKING = "shuttlecock_tracking"
    STRATEGY_ANALYSIS = "strategy_analysis"
    REPORT_GENERATION = "report_generation"
