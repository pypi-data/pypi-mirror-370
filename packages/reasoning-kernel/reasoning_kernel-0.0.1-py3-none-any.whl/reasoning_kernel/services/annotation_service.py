"""
Service for managing collaborative annotations on reasoning chains
"""

from datetime import datetime
from typing import List, Optional

from reasoning_kernel.models.annotations import Annotation
from reasoning_kernel.models.annotations import AnnotationEvent
from reasoning_kernel.models.annotations import AnnotationReply
from reasoning_kernel.models.annotations import AnnotationUpdate
from reasoning_kernel.models.annotations import CreateAnnotationRequest
from reasoning_kernel.models.annotations import User
from reasoning_kernel.services.redis_service import RedisMemoryService
from reasoning_kernel.utils.security import get_secure_logger


logger = get_secure_logger(__name__)

class AnnotationService:
    """Service for managing collaborative annotations"""
    
    def __init__(self, redis_service: RedisMemoryService, db_manager=None):
        self.redis = redis_service
        self.db = db_manager
        self.annotation_prefix = "annotations:"
        self.chain_annotations_prefix = "chain_annotations:"
        self.active_users_prefix = "active_users:"
        
    async def create_annotation(self, request: CreateAnnotationRequest) -> Annotation:
        """Create a new annotation"""
        try:
            annotation = Annotation(
                reasoning_chain_id=request.reasoning_chain_id,
                user=request.user,
                type=request.type,
                target=request.target,
                position=request.position,
                content=request.content
            )
            
            # Store annotation in Redis
            annotation_key = f"{self.annotation_prefix}{annotation.id}"
            await self.redis.store_data(annotation_key, annotation.model_dump(), self.redis.ttl_seconds)
            
            # Add to chain's annotation list
            chain_key = f"{self.chain_annotations_prefix}{request.reasoning_chain_id}"
            # Store as JSON list instead of set for better compatibility
            existing_annotations = await self.redis.get_data(chain_key) or []
            existing_annotations.append(annotation.id)
            await self.redis.store_data(chain_key, existing_annotations, self.redis.ttl_seconds)
            
            # Store in database for persistence
            if self.db:
                await self._store_annotation_in_db(annotation)
            
            # Broadcast real-time event
            await self._broadcast_annotation_event("created", annotation, request.user)
            
            logger.info(f"Created annotation {annotation.id} for chain {request.reasoning_chain_id}")
            return annotation
            
        except Exception as e:
            logger.error(f"Failed to create annotation: {e}")
            raise
    
    async def get_annotations_for_chain(self, reasoning_chain_id: str) -> List[Annotation]:
        """Get all annotations for a reasoning chain"""
        try:
            chain_key = f"{self.chain_annotations_prefix}{reasoning_chain_id}"
            annotation_ids = await self.redis.get_data(chain_key) or []
            
            annotations = []
            for annotation_id in annotation_ids:
                annotation_key = f"{self.annotation_prefix}{annotation_id}"
                annotation_data = await self.redis.get_data(annotation_key)
                if annotation_data:
                    try:
                        annotation = Annotation.model_validate(annotation_data)
                        annotations.append(annotation)
                    except Exception as e:
                        logger.error("Failed to parse annotation %s: %s", annotation_id, e)
                        continue
            
            # Sort by creation time
            annotations.sort(key=lambda a: a.created_at)
            return annotations
            
        except Exception as e:
            logger.error("Failed to get annotations for chain %s: %s", reasoning_chain_id, e)
            return []
    
    async def update_annotation(self, annotation_id: str, update: AnnotationUpdate, user: User) -> Optional[Annotation]:
        """Update an existing annotation"""
        try:
            annotation_key = f"{self.annotation_prefix}{annotation_id}"
            annotation_data = await self.redis.get_data(annotation_key)
            
            if not annotation_data:
                return None
            
            annotation = Annotation.model_validate(annotation_data)
            
            # Update fields
            if update.content is not None:
                annotation.content = update.content
            if update.resolved is not None:
                annotation.resolved = update.resolved
            
            annotation.updated_at = datetime.now()
            
            # Save updated annotation
            await self.redis.set(annotation_key, annotation.model_dump_json())
            
            # Update in database
            if self.db:
                await self._update_annotation_in_db(annotation)
            
            # Broadcast update event
            await self._broadcast_annotation_event("updated", annotation, user)
            
            logger.info(f"Updated annotation {annotation_id}")
            return annotation
            
        except Exception as e:
            sanitized_annotation_id = annotation_id.replace('\r', '').replace('\n', '')
            logger.error(f"Failed to update annotation {sanitized_annotation_id}: {e}")
            return None
    
    async def add_reply(self, annotation_id: str, content: str, user: User) -> Optional[AnnotationReply]:
        """Add a reply to an annotation"""
        try:
            annotation_key = f"{self.annotation_prefix}{annotation_id}"
            annotation_data = await self.redis.get(annotation_key)
            
            if not annotation_data:
                return None
            
            annotation = Annotation.model_validate_json(annotation_data)
            
            reply = AnnotationReply(
                user=user,
                content=content
            )
            
            annotation.replies.append(reply)
            annotation.updated_at = datetime.now()
            
            # Save updated annotation
            await self.redis.set(annotation_key, annotation.model_dump_json())
            
            # Update in database
            if self.db:
                await self._update_annotation_in_db(annotation)
            
            # Broadcast reply event
            await self._broadcast_annotation_event("reply_added", annotation, user)
            
            logger.info(f"Added reply to annotation {annotation_id}")
            return reply
            
        except Exception as e:
            sanitized_annotation_id = annotation_id.replace('\r', '').replace('\n', '')
            logger.error(f"Failed to add reply to annotation {sanitized_annotation_id}: {e}")
            return None
    
    async def vote_annotation(self, annotation_id: str, user_id: str, vote: bool) -> Optional[Annotation]:
        """Vote on an annotation (upvote/downvote)"""
        try:
            annotation_key = f"{self.annotation_prefix}{annotation_id}"
            annotation_data = await self.redis.get(annotation_key)
            
            if not annotation_data:
                return None
            
            annotation = Annotation.model_validate_json(annotation_data)
            
            # Handle voting logic
            if vote and user_id not in annotation.voters:
                annotation.votes += 1
                annotation.voters.append(user_id)
            elif not vote and user_id in annotation.voters:
                annotation.votes -= 1
                annotation.voters.remove(user_id)
            
            # Save updated annotation
            await self.redis.set(annotation_key, annotation.model_dump_json())
            
            # Update in database
            if self.db:
                await self._update_annotation_in_db(annotation)
            
            logger.info(f"User {user_id} voted on annotation {annotation_id}")
            return annotation
            
        except Exception as e:
            sanitized_annotation_id = annotation_id.replace('\r', '').replace('\n', '')
            logger.error(f"Failed to vote on annotation {sanitized_annotation_id}: {e}")
            return None
    
    async def delete_annotation(self, annotation_id: str, user: User) -> bool:
        """Delete an annotation"""
        try:
            annotation_key = f"{self.annotation_prefix}{annotation_id}"
            annotation_data = await self.redis.get(annotation_key)
            
            if not annotation_data:
                return False
            
            annotation = Annotation.model_validate_json(annotation_data)
            
            # Remove from Redis
            await self.redis.delete(annotation_key)
            
            # Remove from chain's annotation list
            chain_key = f"{self.chain_annotations_prefix}{annotation.reasoning_chain_id}"
            await self.redis.srem(chain_key, annotation_id)
            
            # Remove from database
            if self.db:
                await self._delete_annotation_from_db(annotation_id)
            
            # Broadcast delete event
            await self._broadcast_annotation_event("deleted", annotation, user)
            
            logger.info(f"Deleted annotation {annotation_id}")
            return True
            
        except Exception as e:
            sanitized_annotation_id = annotation_id.replace('\r', '').replace('\n', '')
            logger.error(f"Failed to delete annotation {sanitized_annotation_id}: {e}")
            return False
    
    async def get_active_users(self, reasoning_chain_id: str) -> List[User]:
        """Get users currently viewing/annotating a reasoning chain"""
        try:
            users_key = f"{self.active_users_prefix}{reasoning_chain_id}"
            user_data_list = await self.redis.smembers(users_key)
            
            users = []
            for user_data in user_data_list:
                try:
                    user = User.model_validate_json(user_data)
                    users.append(user)
                except Exception:
                    continue
            
            return users
            
        except Exception as e:
            sanitized_chain_id = reasoning_chain_id.replace('\r', '').replace('\n', '')
            logger.error(f"Failed to get active users for chain {sanitized_chain_id}: {e}")
            return []
    
    async def set_user_active(self, reasoning_chain_id: str, user: User, ttl: int = 30):
        """Mark a user as active on a reasoning chain"""
        try:
            users_key = f"{self.active_users_prefix}{reasoning_chain_id}"
            user_data = user.model_dump_json()
            
            # Add user to active set with TTL
            await self.redis.sadd(users_key, user_data)
            await self.redis.expire(users_key, ttl)
            
            logger.debug(f"User {user.id} marked as active on chain {reasoning_chain_id}")
            
        except Exception as e:
            logger.error(f"Failed to mark user active: {e}")
    
    async def _broadcast_annotation_event(self, event_type: str, annotation: Annotation, user: User):
        """Broadcast annotation event to all connected clients"""
        try:
            event = AnnotationEvent(
                event_type=event_type,
                annotation=annotation,
                user=user
            )
            
            # Publish to Redis pub/sub channel
            channel = f"annotations:{annotation.reasoning_chain_id}"
            await self.redis.publish(channel, event.model_dump_json())
            
            logger.debug(f"Broadcasted {event_type} event for annotation {annotation.id}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast annotation event: {e}")
    
    async def _store_annotation_in_db(self, annotation: Annotation):
        """Store annotation in database for persistence"""
        if not self.db:
            return
        
        try:
            # Implementation depends on your database schema
            # This is a placeholder for the actual database storage
            logger.debug(f"Stored annotation {annotation.id} in database")
        except Exception as e:
            logger.error(f"Failed to store annotation in database: {e}")
    
    async def _update_annotation_in_db(self, annotation: Annotation):
        """Update annotation in database"""
        if not self.db:
            return
        
        try:
            # Implementation depends on your database schema
            logger.debug(f"Updated annotation {annotation.id} in database")
        except Exception as e:
            logger.error(f"Failed to update annotation in database: {e}")
    
    async def _delete_annotation_from_db(self, annotation_id: str):
        """Delete annotation from database"""
        if not self.db:
            return
        
        try:
            # Implementation depends on your database schema
            logger.debug(f"Deleted annotation {annotation_id} from database")
        except Exception as e:
            logger.error(f"Failed to delete annotation from database: {e}")