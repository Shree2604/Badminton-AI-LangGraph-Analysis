import asyncio
import concurrent.futures
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
import queue
import logging
import cv2
import numpy as np
import dask
from dask import delayed
from dask.distributed import Client
from typing import List

from utils import ProcessingTask, TaskType
from config import DASK_N_WORKERS, DASK_THREADS_PER_WORKER

class ParallelDataPipeline:
    """
    Manages the parallel ingestion and preprocessing of data streams (video, text).
    Uses Dask for parallel frame extraction from videos.
    """
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or mp.cpu_count()
        self.input_queue = queue.PriorityQueue()
        self.output_queue = queue.Queue()
        self.processing_status = {}
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        try:
            self.dask_client = Client(n_workers=DASK_N_WORKERS, threads_per_worker=DASK_THREADS_PER_WORKER)
        except (ImportError, OSError):
            print("Could not start Dask client. Dask is not installed or configured properly.")
            self.dask_client = None

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    async def process_video_stream(self, video_path: str) -> List[np.ndarray]:
        """
        Parallel video frame extraction and preprocessing using Dask.
        """
        if not self.dask_client:
            self.logger.error("Dask client not available. Cannot process video stream.")
            return []

        @delayed
        def extract_frame_batch(path: str, start_frame: int, batch_size: int):
            """Extracts a batch of frames from a video file."""
            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                return []
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            frames = []
            for _ in range(batch_size):
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
            
            cap.release()
            return frames
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.logger.error(f"Could not open video file: {video_path}")
            return []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        
        batch_size = 30
        batches = []
        
        for start_frame in range(0, total_frames, batch_size):
            batch = extract_frame_batch(video_path, start_frame, batch_size)
            batches.append(batch)
        
        if not batches:
            return []

        results = dask.compute(*batches)
        
        all_frames = [frame for batch_frames in results for frame in batch_frames if frame is not None]
        
        self.logger.info(f"Extracted {len(all_frames)} frames from {video_path}")
        return all_frames
    
    def add_task(self, task: ProcessingTask):
        """Add task to processing queue with priority."""
        self.input_queue.put((task.priority, task.timestamp, task))
        self.logger.info(f"Added task {task.task_id} ({task.task_type}) to queue")
    
    async def process_tasks_parallel(self):
        """
        Process tasks in parallel using asyncio and thread pools.
        """
        
        async def worker():
            while True:
                try:
                    priority, timestamp, task = self.input_queue.get_nowait()
                    
                    self.logger.info(f"Processing task {task.task_id} ({task.task_type})")
                    await asyncio.sleep(1)
                    result = {"status": "completed", "data": f"processed_data_for_{task.task_id}"}
                    
                    self.output_queue.put((task.task_id, result))
                    self.logger.info(f"Completed task {task.task_id}")
                    
                except queue.Empty:
                    await asyncio.sleep(0.1)
                except Exception as e:
                    self.logger.error(f"Error processing task: {e}", exc_info=True)
        
        workers = [asyncio.create_task(worker()) for _ in range(self.max_workers)]
        await asyncio.gather(*workers)

    def shutdown(self):
        """Shutdown the pipeline and its resources."""
        self.executor.shutdown(wait=True)
        if self.dask_client:
            self.dask_client.close()
        self.logger.info("Data pipeline has been shut down.")
