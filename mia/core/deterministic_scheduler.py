#!/usr/bin/env python3
"""
Deterministic Scheduler
"""

import threading
import time
from typing import Callable, Any, List, Dict
from queue import PriorityQueue
from dataclasses import dataclass

@dataclass
class DeterministicTask:
    """Deterministična naloga"""
    priority: int
    order: int
    task_id: str
    function: Callable
    args: tuple
    kwargs: dict

class DeterministicScheduler:
    """Deterministični scheduler"""
    
    def __init__(self, deterministic_seed: int = 42):
        self.deterministic_seed = deterministic_seed
        self.task_queue = PriorityQueue()
        self.execution_order = []
        self.task_counter = 0
        self.running = False
        self.worker_thread = None
        
    def schedule_task(self, function: Callable, priority: int = 0, *args, **kwargs) -> str:
        """Razporedi nalogo deterministično"""
        task_id = f"task_{self.task_counter}_{self.deterministic_seed}"
        
        task = DeterministicTask(
            priority=priority,
            order=self.task_counter,
            task_id=task_id,
            function=function,
            args=args,
            kwargs=kwargs
        )
        
        # Dodaj v priority queue (deterministični vrstni red)
        self.task_queue.put((priority, self.task_counter, task))
        self.task_counter += 1
        
        return task_id
    
    def start_deterministic_execution(self):
        """Začni deterministično izvajanje"""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._execute_tasks_deterministic)
            self.worker_thread.daemon = True
            self.worker_thread.start()
    
    def _execute_tasks_deterministic(self):
        """Izvajaj naloge deterministično"""
        while self.running:
            try:
                if not self.task_queue.empty():
                    priority, order, task = self.task_queue.get(timeout=1)
                    
                    # Izvedi nalogo
                    try:
                        result = task.function(*task.args, **task.kwargs)
                        self.execution_order.append({
                            "task_id": task.task_id,
                            "priority": priority,
                            "order": order,
                            "result": str(result)[:100]  # Omeji dolžino
                        })
                    except Exception as e:
                        self.execution_order.append({
                            "task_id": task.task_id,
                            "priority": priority,
                            "order": order,
                            "error": str(e)
                        })
                    
                    self.task_queue.task_done()
                else:
                    time.sleep(0.01)  # Kratka pavza
                    
            except Exception as e:
                # Ignoriraj timeout napake
                pass
    
    def stop_execution(self):
        """Ustavi izvajanje"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
    
    def get_execution_hash(self) -> str:
        """Pridobi hash izvajanja"""
        import hashlib
        import json
        
        execution_data = {
            "execution_order": self.execution_order,
            "seed": self.deterministic_seed,
            "task_count": self.task_counter
        }
        
        data_str = json.dumps(execution_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(data_str.encode()).hexdigest()
