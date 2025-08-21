"""
Adaptive Learning System
========================

Learns from user feedback and improves reasoning quality over time.
"""

from collections import defaultdict
from dataclasses import asdict
from dataclasses import dataclass
import time
from typing import Any, Dict, List, Optional

import structlog


logger = structlog.get_logger(__name__)

@dataclass
class UserFeedback:
    """User feedback on reasoning quality"""
    session_id: str
    reasoning_stage: str  # 'parse', 'retrieve', 'graph', 'synthesize', 'infer', 'overall'
    rating: float  # 1-5 scale
    feedback_type: str  # 'accuracy', 'relevance', 'clarity', 'completeness'
    comments: Optional[str] = None
    timestamp: float = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class ReasoningPattern:
    """Represents a learned reasoning pattern"""
    pattern_id: str
    context_features: Dict[str, Any]
    successful_strategies: List[str]
    failed_strategies: List[str]
    confidence_threshold: float
    success_rate: float
    usage_count: int
    last_updated: float

@dataclass
class UserProfile:
    """User's personalized reasoning preferences"""
    user_id: str
    preferred_detail_level: str  # 'brief', 'moderate', 'detailed'
    preferred_uncertainty_style: str  # 'conservative', 'balanced', 'optimistic'
    domain_expertise: Dict[str, float]  # Domain -> expertise level
    feedback_patterns: Dict[str, float]  # What they typically rate highly
    learning_preferences: Dict[str, Any]
    created_at: float
    last_updated: float

class AdaptiveLearningSystem:
    """Learns from feedback and adapts reasoning strategies"""
    
    def __init__(self, redis_service=None, database_manager=None):
        self.redis_service = redis_service
        self.database_manager = database_manager
        self.feedback_history = []
        self.learned_patterns = {}
        self.user_profiles = {}
        
    async def record_feedback(self, feedback: UserFeedback) -> bool:
        """Record user feedback for learning"""
        try:
            # Store feedback
            self.feedback_history.append(feedback)
            
            # Store in Redis for fast access
            if self.redis_service:
                feedback_key = f"feedback:{feedback.session_id}:{feedback.reasoning_stage}"
                await self.redis_service.set_data(feedback_key, asdict(feedback), ttl=86400)
            
            # Store in database for long-term learning
            if self.database_manager:
                await self._store_feedback_in_db(feedback)
            
            # Update learning patterns
            await self._update_learning_patterns(feedback)
            
            # Update user profile if available
            if feedback.user_id:
                await self._update_user_profile(feedback)
            
            logger.info("Feedback recorded successfully",
                       session_id=feedback.session_id,
                       stage=feedback.reasoning_stage,
                       rating=feedback.rating)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return False
    
    async def get_personalized_recommendations(self, user_id: str, 
                                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Get personalized reasoning recommendations for a user"""
        
        profile = await self._get_user_profile(user_id)
        if not profile:
            # Create default profile
            profile = UserProfile(
                user_id=user_id,
                preferred_detail_level='moderate',
                preferred_uncertainty_style='balanced',
                domain_expertise={},
                feedback_patterns={},
                learning_preferences={},
                created_at=time.time(),
                last_updated=time.time()
            )
        
        recommendations = {
            'detail_level': profile.preferred_detail_level,
            'uncertainty_style': profile.preferred_uncertainty_style,
            'suggested_models': self._suggest_models_for_user(profile, context),
            'confidence_threshold': self._get_optimal_confidence_threshold(profile),
            'explanation_style': self._get_explanation_style(profile),
            'focus_areas': self._identify_focus_areas(profile, context)
        }
        
        return recommendations
    
    async def analyze_reasoning_success_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in successful vs unsuccessful reasoning"""
        
        success_patterns = defaultdict(list)
        failure_patterns = defaultdict(list)
        
        # Analyze feedback history
        for feedback in self.feedback_history:
            pattern_key = f"{feedback.reasoning_stage}_{feedback.feedback_type}"
            
            if feedback.rating >= 4.0:  # Success threshold
                success_patterns[pattern_key].append(feedback)
            elif feedback.rating <= 2.0:  # Failure threshold
                failure_patterns[pattern_key].append(feedback)
        
        # Generate insights
        insights = {
            'successful_strategies': {},
            'problematic_areas': {},
            'improvement_opportunities': [],
            'confidence_calibration': {},
            'user_satisfaction_trends': {}
        }
        
        # Analyze successful strategies
        for pattern, feedbacks in success_patterns.items():
            if len(feedbacks) >= 3:  # Minimum sample size
                avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
                insights['successful_strategies'][pattern] = {
                    'average_rating': avg_rating,
                    'count': len(feedbacks),
                    'common_features': self._extract_common_features(feedbacks)
                }
        
        # Analyze problematic areas
        for pattern, feedbacks in failure_patterns.items():
            if len(feedbacks) >= 2:
                avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
                insights['problematic_areas'][pattern] = {
                    'average_rating': avg_rating,
                    'count': len(feedbacks),
                    'common_issues': self._extract_common_issues(feedbacks)
                }
        
        # Generate improvement opportunities
        insights['improvement_opportunities'] = self._generate_improvement_suggestions(
            success_patterns, failure_patterns
        )
        
        return insights
    
    async def optimize_model_selection(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Optimize model selection based on learned patterns"""
        
        # Default model selection
        optimal_models = {
            'parse_model': 'gemini-2.5-pro',
            'graph_model': 'phi-4-reasoning', 
            'synthesis_model': 'gemini-2.5-pro'
        }
        
        # Check for learned patterns that match current context
        context_features = self._extract_context_features(context)
        
        for pattern in self.learned_patterns.values():
            if self._context_matches_pattern(context_features, pattern.context_features):
                if pattern.success_rate > 0.7:  # High success threshold
                    # Apply successful strategies from this pattern
                    for strategy in pattern.successful_strategies:
                        if strategy.startswith('model:'):
                            model_assignment = strategy.replace('model:', '')
                            if ':' in model_assignment:
                                stage, model = model_assignment.split(':', 1)
                                if stage in optimal_models:
                                    optimal_models[stage] = model
        
        logger.info("Model selection optimized based on learned patterns",
                   models=optimal_models)
        
        return optimal_models
    
    async def get_confidence_calibration(self) -> Dict[str, float]:
        """Get confidence calibration adjustments based on historical accuracy"""
        
        calibration = {
            'parse': 0.0,
            'retrieve': 0.0,
            'graph': 0.0,
            'synthesize': 0.0,
            'infer': 0.0
        }
        
        # Analyze feedback to determine if confidence scores are well-calibrated
        stage_feedback = defaultdict(list)
        
        for feedback in self.feedback_history:
            if feedback.feedback_type == 'accuracy':
                stage_feedback[feedback.reasoning_stage].append(feedback)
        
        for stage, feedbacks in stage_feedback.items():
            if len(feedbacks) >= 5:  # Minimum sample for calibration
                # Calculate average difference between predicted confidence and actual accuracy
                accuracy_ratings = [f.rating / 5.0 for f in feedbacks]  # Normalize to 0-1
                
                # If we consistently over-predict confidence, adjust downward
                avg_accuracy = sum(accuracy_ratings) / len(accuracy_ratings)
                
                if avg_accuracy < 0.6:  # Low accuracy suggests overconfidence
                    calibration[stage] = -0.1  # Reduce confidence
                elif avg_accuracy > 0.9:  # High accuracy suggests underconfidence
                    calibration[stage] = 0.05  # Increase confidence slightly
        
        return calibration
    
    async def _store_feedback_in_db(self, feedback: UserFeedback):
        """Store feedback in database for long-term learning"""
        try:
            query = """
            INSERT INTO user_feedback 
            (session_id, reasoning_stage, rating, feedback_type, comments, timestamp, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            await self.database_manager.execute_query(
                query,
                (feedback.session_id, feedback.reasoning_stage, feedback.rating,
                 feedback.feedback_type, feedback.comments, feedback.timestamp, feedback.user_id)
            )
        except Exception as e:
            logger.warning(f"Could not store feedback in database: {e}")
    
    async def _update_learning_patterns(self, feedback: UserFeedback):
        """Update learned patterns based on new feedback"""
        
        # Create pattern key based on context
        pattern_key = f"{feedback.reasoning_stage}_{feedback.feedback_type}"
        
        if pattern_key not in self.learned_patterns:
            self.learned_patterns[pattern_key] = ReasoningPattern(
                pattern_id=pattern_key,
                context_features={},
                successful_strategies=[],
                failed_strategies=[],
                confidence_threshold=0.7,
                success_rate=0.5,
                usage_count=0,
                last_updated=time.time()
            )
        
        pattern = self.learned_patterns[pattern_key]
        pattern.usage_count += 1
        pattern.last_updated = time.time()
        
        # Update success rate
        total_feedback = len([f for f in self.feedback_history 
                            if f.reasoning_stage == feedback.reasoning_stage 
                            and f.feedback_type == feedback.feedback_type])
        
        successful_feedback = len([f for f in self.feedback_history 
                                 if f.reasoning_stage == feedback.reasoning_stage 
                                 and f.feedback_type == feedback.feedback_type 
                                 and f.rating >= 4.0])
        
        if total_feedback > 0:
            pattern.success_rate = successful_feedback / total_feedback
    
    async def _update_user_profile(self, feedback: UserFeedback):
        """Update user profile based on feedback"""
        
        if feedback.user_id not in self.user_profiles:
            self.user_profiles[feedback.user_id] = UserProfile(
                user_id=feedback.user_id,
                preferred_detail_level='moderate',
                preferred_uncertainty_style='balanced',
                domain_expertise={},
                feedback_patterns={},
                learning_preferences={},
                created_at=time.time(),
                last_updated=time.time()
            )
        
        profile = self.user_profiles[feedback.user_id]
        profile.last_updated = time.time()
        
        # Update feedback patterns
        pattern_key = f"{feedback.reasoning_stage}_{feedback.feedback_type}"
        if pattern_key not in profile.feedback_patterns:
            profile.feedback_patterns[pattern_key] = []
        
        profile.feedback_patterns[pattern_key] = feedback.rating
    
    async def _get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile from cache or database"""
        
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        # Try to load from Redis
        if self.redis_service:
            try:
                profile_data = await self.redis_service.get_data(f"user_profile:{user_id}")
                if profile_data:
                    return UserProfile(**profile_data)
            except Exception as e:
                logger.warning(f"Could not load user profile from Redis: {e}")
        
        return None
    
    def _suggest_models_for_user(self, profile: UserProfile, context: Dict[str, Any]) -> Dict[str, str]:
        """Suggest optimal models based on user profile and context"""
        
        suggestions = {
            'parse_model': 'gemini-2.5-pro',
            'graph_model': 'phi-4-reasoning',
            'synthesis_model': 'gemini-2.5-pro'
        }
        
        # Adjust based on user preferences
        if profile.preferred_detail_level == 'detailed':
            suggestions['parse_model'] = 'gemini-2.5-pro'  # More detailed parsing
        elif profile.preferred_detail_level == 'brief':
            suggestions['parse_model'] = 'azure-gpt-5-mini'  # Faster, more concise
        
        return suggestions
    
    def _get_optimal_confidence_threshold(self, profile: UserProfile) -> float:
        """Get optimal confidence threshold for user"""
        
        base_threshold = 0.7
        
        # Adjust based on user's uncertainty style
        if profile.preferred_uncertainty_style == 'conservative':
            return base_threshold + 0.1
        elif profile.preferred_uncertainty_style == 'optimistic':
            return base_threshold - 0.1
        
        return base_threshold
    
    def _get_explanation_style(self, profile: UserProfile) -> Dict[str, Any]:
        """Get explanation style preferences for user"""
        
        return {
            'verbosity': profile.preferred_detail_level,
            'technical_level': 'moderate',  # Could be learned from feedback
            'include_uncertainty': True,
            'show_reasoning_steps': profile.preferred_detail_level != 'brief'
        }
    
    def _identify_focus_areas(self, profile: UserProfile, context: Dict[str, Any]) -> List[str]:
        """Identify areas that need extra attention for this user"""
        
        focus_areas = []
        
        # Check user's historical weak points
        for pattern, rating in profile.feedback_patterns.items():
            if rating < 3.0:  # Below average rating
                focus_areas.append(pattern.replace('_', ' ').title())
        
        return focus_areas[:3]  # Top 3 focus areas
    
    def _extract_common_features(self, feedbacks: List[UserFeedback]) -> List[str]:
        """Extract common features from successful feedback"""
        # This would analyze the reasoning sessions that received positive feedback
        # For now, return placeholder
        return ['high_confidence', 'clear_explanations', 'relevant_evidence']
    
    def _extract_common_issues(self, feedbacks: List[UserFeedback]) -> List[str]:
        """Extract common issues from negative feedback"""
        issues = []
        
        # Analyze comments for common themes
        for feedback in feedbacks:
            if feedback.comments:
                comment_lower = feedback.comments.lower()
                if 'unclear' in comment_lower or 'confusing' in comment_lower:
                    issues.append('clarity_issues')
                if 'incomplete' in comment_lower or 'missing' in comment_lower:
                    issues.append('completeness_issues')
                if 'wrong' in comment_lower or 'incorrect' in comment_lower:
                    issues.append('accuracy_issues')
        
        return list(set(issues))
    
    def _generate_improvement_suggestions(self, success_patterns: Dict, 
                                        failure_patterns: Dict) -> List[str]:
        """Generate suggestions for system improvement"""
        
        suggestions = []
        
        # Compare success vs failure patterns
        all_stages = set()
        for pattern in success_patterns.keys():
            all_stages.add(pattern.split('_')[0])
        for pattern in failure_patterns.keys():
            all_stages.add(pattern.split('_')[0])
        
        for stage in all_stages:
            success_count = len([p for p in success_patterns.keys() if p.startswith(stage)])
            failure_count = len([p for p in failure_patterns.keys() if p.startswith(stage)])
            
            if failure_count > success_count:
                suggestions.append(f"Improve {stage} stage - frequent user dissatisfaction")
        
        return suggestions
    
    def _extract_context_features(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant features from reasoning context"""
        
        features = {}
        
        # Extract domain
        if 'domain' in context:
            features['domain'] = context['domain']
        
        # Extract complexity indicators
        if 'input_length' in context:
            features['complexity'] = 'high' if context['input_length'] > 1000 else 'low'
        
        # Extract data availability
        if 'has_data' in context:
            features['data_available'] = context['has_data']
        
        return features
    
    def _context_matches_pattern(self, context_features: Dict[str, Any], 
                               pattern_features: Dict[str, Any]) -> bool:
        """Check if current context matches a learned pattern"""
        
        # Simple matching - could be made more sophisticated
        matches = 0
        total_features = len(pattern_features)
        
        if total_features == 0:
            return False
        
        for key, value in pattern_features.items():
            if key in context_features and context_features[key] == value:
                matches += 1
        
        # Return true if at least 70% of features match
        return (matches / total_features) >= 0.7