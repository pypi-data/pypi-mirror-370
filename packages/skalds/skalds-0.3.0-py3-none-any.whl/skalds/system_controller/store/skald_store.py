"""
SkaldStore Module

In-memory storage for Skalds information including status, heartbeats, and task assignments.
Based on the reference implementation but enhanced for SystemController use.
"""

from typing import Dict, List, Optional
import threading
import time
from skalds.model.task import TaskWorkerSimpleMap
from skalds.utils.logging import logger


class SkaldData:
    """
    Data structure for storing Skalds information.
    
    Attributes:
        id: Unique Skalds identifier
        update_time: Last update timestamp in milliseconds
        heartbeat: Current heartbeat value
        mode: Skalds mode (node/edge)
        all_tasks: List of tasks assigned to this Skalds
    """
    
    def __init__(self, id: str, update_time: int, mode: str = "node"):
        self.id = id
        self.update_time = update_time
        self.heartbeat = 0
        self.mode = mode  # node or edge
        self.all_tasks: List[TaskWorkerSimpleMap] = []
        self.supported_tasks: List[str] = []
        self._lock = threading.RLock()

    def update_update_time(self, new_update_time: int) -> None:
        """Update the last update timestamp."""
        with self._lock:
            self.update_time = new_update_time

    def update_heartbeat(self, new_heartbeat: int) -> None:
        """Update the heartbeat value."""
        with self._lock:
            self.heartbeat = new_heartbeat

    def update_tasks(self, new_tasks: List[TaskWorkerSimpleMap]) -> None:
        """Update the list of assigned tasks."""
        with self._lock:
            self.all_tasks = new_tasks.copy() if new_tasks else []

    def update_supported_tasks(self, new_supported_tasks: List[str]) -> None:
        """Update the list of supported task class names."""
        with self._lock:
            self.supported_tasks = new_supported_tasks.copy() if new_supported_tasks else []

    def get_task_count(self) -> int:
        """Get the number of tasks assigned to this Skalds."""
        with self._lock:
            return len(self.all_tasks)

    def is_online(self, timeout_ms: int = 10000) -> bool:
        """Check if Skalds is considered online based on update time."""
        current_time = int(time.time() * 1000)
        with self._lock:
            return (current_time - self.update_time) <= timeout_ms

    def to_dict(self) -> Dict:
        """Convert SkaldData to dictionary for API responses."""
        with self._lock:
            return {
                "id": self.id,
                "type": self.mode,
                "status": "online" if self.is_online() else "offline",
                "lastHeartbeat": self.update_time,
                "supportedTasks": self.supported_tasks.copy(),
                "currentTasks": [task.id for task in self.all_tasks],
                "heartbeat": self.heartbeat,
                "taskCount": len(self.all_tasks)
            }


class SkaldStore:
    """
    Thread-safe in-memory store for Skalds information.
    
    This store maintains information about all Skalds in the system,
    including their status, heartbeats, and task assignments.
    """
    
    def __init__(self):
        self.all_skalds: Dict[str, SkaldData] = {}
        self._store_lock = threading.RLock()
        logger.info("SkaldStore initialized")

    def add_skald(self, skald_id: str, update_time: int, mode: str = "node") -> None:
        """
        Add a new Skalds to the store.
        
        Args:
            skald_id: Unique identifier for the Skalds
            update_time: Initial update timestamp
            mode: Skalds mode (node/edge)
        """
        with self._store_lock:
            if skald_id not in self.all_skalds:
                self.all_skalds[skald_id] = SkaldData(skald_id, update_time, mode)
                logger.info(f"Added Skalds: {skald_id} (mode: {mode})")
            else:
                # Update existing Skalds's update time
                self.all_skalds[skald_id].update_update_time(update_time)

    def update_skald_update_time(self, skald_id: str, new_update_time: int) -> None:
        """Update the last update time for a Skalds."""
        with self._store_lock:
            if skald_id in self.all_skalds:
                self.all_skalds[skald_id].update_update_time(new_update_time)

    def update_skald_heartbeat(self, skald_id: str, new_heartbeat: int) -> None:
        """Update the heartbeat for a Skalds."""
        with self._store_lock:
            if skald_id in self.all_skalds:
                self.all_skalds[skald_id].update_heartbeat(new_heartbeat)

    def update_skald_tasks(self, skald_id: str, new_tasks: List[TaskWorkerSimpleMap]) -> None:
        """Update the task list for a Skalds."""
        with self._store_lock:
            if skald_id in self.all_skalds:
                self.all_skalds[skald_id].update_tasks(new_tasks)

    def update_skald_supported_tasks(self, skald_id: str, new_supported_tasks: List[str]) -> None:
        """Update the supported task class names for a Skalds."""
        with self._store_lock:
            if skald_id in self.all_skalds:
                self.all_skalds[skald_id].update_supported_tasks(new_supported_tasks)

    def update_skald_mode(self, skald_id: str, mode: str) -> None:
        """Update the mode for a Skalds."""
        with self._store_lock:
            if skald_id in self.all_skalds:
                self.all_skalds[skald_id].mode = mode

    def get_skald(self, skald_id: str) -> Optional[SkaldData]:
        """Get a specific Skalds by ID."""
        with self._store_lock:
            return self.all_skalds.get(skald_id)

    def get_all_skalds(self) -> Dict[str, SkaldData]:
        """Get all Skalds in the store."""
        with self._store_lock:
            return self.all_skalds.copy()

    def get_online_skalds(self, timeout_ms: int = 10000) -> Dict[str, SkaldData]:
        """Get all online Skalds."""
        with self._store_lock:
            return {
                skald_id: skald_data 
                for skald_id, skald_data in self.all_skalds.items()
                if skald_data.is_online(timeout_ms)
            }

    def get_node_skalds(self) -> Dict[str, SkaldData]:
        """Get all node-type Skalds (can be assigned tasks)."""
        with self._store_lock:
            return {
                skald_id: skald_data 
                for skald_id, skald_data in self.all_skalds.items()
                if skald_data.mode == "node" and skald_data.is_online()
            }

    def get_least_busy_skald(self) -> Optional[str]:
        """Get the Skalds ID with the least number of tasks."""
        node_skalds = self.get_node_skalds()
        if not node_skalds:
            return None
        
        return min(node_skalds.keys(), key=lambda x: node_skalds[x].get_task_count())

    def del_skald(self, skald_id: str) -> None:
        """Remove a Skalds from the store."""
        with self._store_lock:
            if skald_id in self.all_skalds:
                del self.all_skalds[skald_id]
                logger.info(f"Removed Skalds: {skald_id}")

    def clear(self) -> None:
        """Clear all Skalds from the store."""
        with self._store_lock:
            self.all_skalds.clear()
            logger.info("SkaldStore cleared")

    def get_summary(self) -> Dict:
        """Get summary statistics for dashboard."""
        with self._store_lock:
            online_skalds = self.get_online_skalds()
            total_tasks = sum(skalds.get_task_count() for skalds in self.all_skalds.values())
            
            return {
                "totalSkalds": len(self.all_skalds),
                "onlineSkalds": len(online_skalds),
                "totalRunningTasks": total_tasks,
                "nodeSkalds": len([s for s in self.all_skalds.values() if s.mode == "node"]),
                "edgeSkalds": len([s for s in self.all_skalds.values() if s.mode == "edge"])
            }

    def to_api_format(self) -> List[Dict]:
        """Convert all Skalds to API response format."""
        with self._store_lock:
            return [skalds.to_dict() for skalds in self.all_skalds.values()]