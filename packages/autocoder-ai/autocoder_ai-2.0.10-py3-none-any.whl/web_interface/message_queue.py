"""
Message Queue system for offline agents and message persistence
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque, defaultdict
import threading
import pickle
import os
from pathlib import Path

from utils.logger import setup_logger

logger = setup_logger()


class MessageQueue:
    """In-memory message queue with optional persistence"""
    
    def __init__(self, max_size: int = 10000, persist_path: str = None):
        """
        Initialize the message queue
        
        Args:
            max_size: Maximum messages per queue
            persist_path: Optional path to persist messages
        """
        self.queues: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_size))
        self.max_size = max_size
        self.persist_path = persist_path
        self.lock = threading.RLock()
        
        # Message statistics
        self.stats = {
            "total_enqueued": 0,
            "total_dequeued": 0,
            "total_expired": 0,
            "total_failed": 0
        }
        
        # Load persisted messages if path provided
        if persist_path:
            self._load_persisted_messages()
    
    def enqueue(self, queue_name: str, message: Dict[str, Any], 
                ttl_seconds: int = 3600) -> bool:
        """
        Add a message to the queue
        
        Args:
            queue_name: Name of the queue (e.g., session_id)
            message: Message data
            ttl_seconds: Time to live in seconds
            
        Returns:
            True if message was queued successfully
        """
        try:
            with self.lock:
                # Add metadata
                message_wrapper = {
                    "id": f"{queue_name}_{datetime.utcnow().timestamp()}",
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "expires_at": (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat(),
                    "attempts": 0
                }
                
                self.queues[queue_name].append(message_wrapper)
                self.stats["total_enqueued"] += 1
                
                # Persist if enabled
                if self.persist_path:
                    self._persist_queue(queue_name)
                
                logger.debug(f"Message enqueued to {queue_name}: {message.get('type')}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to enqueue message: {e}")
            self.stats["total_failed"] += 1
            return False
    
    def dequeue(self, queue_name: str, count: int = 1) -> List[Dict[str, Any]]:
        """
        Retrieve messages from the queue
        
        Args:
            queue_name: Name of the queue
            count: Number of messages to retrieve
            
        Returns:
            List of messages
        """
        messages = []
        
        try:
            with self.lock:
                queue = self.queues.get(queue_name)
                if not queue:
                    return messages
                
                # Remove expired messages first
                self._cleanup_expired(queue_name)
                
                # Dequeue requested messages
                for _ in range(min(count, len(queue))):
                    if queue:
                        message_wrapper = queue.popleft()
                        message_wrapper["attempts"] += 1
                        messages.append(message_wrapper["message"])
                        self.stats["total_dequeued"] += 1
                
                # Persist changes if enabled
                if self.persist_path and messages:
                    self._persist_queue(queue_name)
                
                logger.debug(f"Dequeued {len(messages)} messages from {queue_name}")
                
        except Exception as e:
            logger.error(f"Failed to dequeue messages: {e}")
            
        return messages
    
    def peek(self, queue_name: str, count: int = 1) -> List[Dict[str, Any]]:
        """
        Peek at messages without removing them
        
        Args:
            queue_name: Name of the queue
            count: Number of messages to peek
            
        Returns:
            List of messages
        """
        messages = []
        
        try:
            with self.lock:
                queue = self.queues.get(queue_name)
                if not queue:
                    return messages
                
                # Remove expired messages first
                self._cleanup_expired(queue_name)
                
                # Peek at messages
                for i, message_wrapper in enumerate(queue):
                    if i >= count:
                        break
                    messages.append(message_wrapper["message"])
                
        except Exception as e:
            logger.error(f"Failed to peek messages: {e}")
            
        return messages
    
    def get_queue_size(self, queue_name: str) -> int:
        """Get the current size of a queue"""
        with self.lock:
            self._cleanup_expired(queue_name)
            return len(self.queues.get(queue_name, []))
    
    def get_all_queue_sizes(self) -> Dict[str, int]:
        """Get sizes of all queues"""
        with self.lock:
            sizes = {}
            for queue_name in list(self.queues.keys()):
                self._cleanup_expired(queue_name)
                sizes[queue_name] = len(self.queues[queue_name])
            return sizes
    
    def clear_queue(self, queue_name: str) -> int:
        """
        Clear all messages from a queue
        
        Returns:
            Number of messages cleared
        """
        with self.lock:
            queue = self.queues.get(queue_name)
            if queue:
                count = len(queue)
                queue.clear()
                
                # Remove persisted queue if enabled
                if self.persist_path:
                    self._remove_persisted_queue(queue_name)
                
                logger.info(f"Cleared {count} messages from queue {queue_name}")
                return count
            return 0
    
    def _cleanup_expired(self, queue_name: str):
        """Remove expired messages from a queue"""
        queue = self.queues.get(queue_name)
        if not queue:
            return
        
        now = datetime.utcnow()
        expired_count = 0
        
        # Create new queue without expired messages
        new_queue = deque(maxlen=self.max_size)
        for message_wrapper in queue:
            expires_at = datetime.fromisoformat(message_wrapper["expires_at"])
            if expires_at > now:
                new_queue.append(message_wrapper)
            else:
                expired_count += 1
        
        if expired_count > 0:
            self.queues[queue_name] = new_queue
            self.stats["total_expired"] += expired_count
            logger.debug(f"Removed {expired_count} expired messages from {queue_name}")
    
    def _persist_queue(self, queue_name: str):
        """Persist a queue to disk"""
        if not self.persist_path:
            return
        
        try:
            persist_dir = Path(self.persist_path)
            persist_dir.mkdir(parents=True, exist_ok=True)
            
            queue_file = persist_dir / f"{queue_name}.pkl"
            queue_data = list(self.queues[queue_name])
            
            with open(queue_file, 'wb') as f:
                pickle.dump(queue_data, f)
                
        except Exception as e:
            logger.error(f"Failed to persist queue {queue_name}: {e}")
    
    def _remove_persisted_queue(self, queue_name: str):
        """Remove a persisted queue file"""
        if not self.persist_path:
            return
        
        try:
            queue_file = Path(self.persist_path) / f"{queue_name}.pkl"
            if queue_file.exists():
                queue_file.unlink()
                
        except Exception as e:
            logger.error(f"Failed to remove persisted queue {queue_name}: {e}")
    
    def _load_persisted_messages(self):
        """Load persisted messages from disk"""
        if not self.persist_path:
            return
        
        try:
            persist_dir = Path(self.persist_path)
            if not persist_dir.exists():
                return
            
            for queue_file in persist_dir.glob("*.pkl"):
                queue_name = queue_file.stem
                
                try:
                    with open(queue_file, 'rb') as f:
                        queue_data = pickle.load(f)
                        self.queues[queue_name] = deque(queue_data, maxlen=self.max_size)
                        logger.info(f"Loaded {len(queue_data)} messages for queue {queue_name}")
                        
                except Exception as e:
                    logger.error(f"Failed to load queue {queue_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load persisted messages: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            return {
                **self.stats,
                "total_queues": len(self.queues),
                "total_messages": sum(len(q) for q in self.queues.values()),
                "queue_sizes": self.get_all_queue_sizes()
            }


class PriorityMessageQueue(MessageQueue):
    """Message queue with priority support"""
    
    def __init__(self, max_size: int = 10000, persist_path: str = None):
        super().__init__(max_size, persist_path)
        # Override queues with priority queues
        self.queues: Dict[str, List[deque]] = defaultdict(
            lambda: [deque(maxlen=max_size) for _ in range(3)]  # 3 priority levels
        )
    
    def enqueue(self, queue_name: str, message: Dict[str, Any], 
                ttl_seconds: int = 3600, priority: int = 1) -> bool:
        """
        Add a message to the queue with priority
        
        Args:
            queue_name: Name of the queue
            message: Message data
            ttl_seconds: Time to live in seconds
            priority: Priority level (0=high, 1=normal, 2=low)
            
        Returns:
            True if message was queued successfully
        """
        if priority not in [0, 1, 2]:
            priority = 1  # Default to normal priority
        
        try:
            with self.lock:
                message_wrapper = {
                    "id": f"{queue_name}_{datetime.utcnow().timestamp()}",
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "expires_at": (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat(),
                    "priority": priority,
                    "attempts": 0
                }
                
                self.queues[queue_name][priority].append(message_wrapper)
                self.stats["total_enqueued"] += 1
                
                if self.persist_path:
                    self._persist_queue(queue_name)
                
                logger.debug(f"Message enqueued to {queue_name} with priority {priority}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to enqueue priority message: {e}")
            self.stats["total_failed"] += 1
            return False
    
    def dequeue(self, queue_name: str, count: int = 1) -> List[Dict[str, Any]]:
        """
        Retrieve messages from the queue in priority order
        
        Args:
            queue_name: Name of the queue
            count: Number of messages to retrieve
            
        Returns:
            List of messages
        """
        messages = []
        
        try:
            with self.lock:
                priority_queues = self.queues.get(queue_name)
                if not priority_queues:
                    return messages
                
                # Process queues in priority order (0=high, 1=normal, 2=low)
                for priority in range(3):
                    queue = priority_queues[priority]
                    
                    while queue and len(messages) < count:
                        message_wrapper = queue.popleft()
                        
                        # Check if expired
                        expires_at = datetime.fromisoformat(message_wrapper["expires_at"])
                        if expires_at > datetime.utcnow():
                            message_wrapper["attempts"] += 1
                            messages.append(message_wrapper["message"])
                            self.stats["total_dequeued"] += 1
                        else:
                            self.stats["total_expired"] += 1
                    
                    if len(messages) >= count:
                        break
                
                if self.persist_path and messages:
                    self._persist_queue(queue_name)
                
                logger.debug(f"Dequeued {len(messages)} priority messages from {queue_name}")
                
        except Exception as e:
            logger.error(f"Failed to dequeue priority messages: {e}")
            
        return messages


# Global message queue instance
message_queue = PriorityMessageQueue(persist_path="data/message_queue")
