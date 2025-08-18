"""
Enhanced Agent with Intelligent Memory Management

This module provides an enhanced version of SingleAgent with:
- Token-aware context management
- Intelligent conversation summarization
- Session cleanup and cost optimization
- Better CLI conversation memory
"""

import os
import time
from typing import Dict, List, Any, Optional, Union
import json

from .agent import SingleAgent
from ..memory.enhanced_memory_manager import EnhancedMemoryManager, MemoryConfig
from .llm_interface import get_llm

class EnhancedSingleAgent(SingleAgent):
    """
    Enhanced SingleAgent with intelligent memory management
    """
    
    def __init__(
        self,
        use_titans_memory: bool = True,
        tools: Optional[List[Any]] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        memory_path: Optional[str] = None,
        enhanced_processing: bool = True,
        config=None,
        memory_config: Optional[MemoryConfig] = None
    ):
        """
        Initialize enhanced agent with intelligent memory management
        
        Args:
            memory_config: Configuration for enhanced memory management
            (other args same as SingleAgent)
        """
        # Initialize parent class
        super().__init__(
            use_titans_memory=use_titans_memory,
            tools=tools,
            llm_provider=llm_provider,
            llm_model=llm_model,
            memory_path=memory_path,
            enhanced_processing=enhanced_processing,
            config=config
        )
        
        # Replace standard memory with enhanced memory manager
        self.enhanced_memory = EnhancedMemoryManager(
            db_path=self.memory_path,
            config=memory_config or MemoryConfig()
        )
        
        print(f"+ Enhanced memory management initialized")
        print(f"  - Max context tokens: {self.enhanced_memory.config.max_context_tokens}")
        print(f"  - Summarization threshold: {self.enhanced_memory.config.summarization_threshold}")
        print(f"  - Session timeout: {self.enhanced_memory.config.session_timeout_hours}h")
    
    def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        tool_name: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Process query with enhanced memory management
        
        Args:
            query: User query
            session_id: Session identifier
            tool_name: Name of tool to use (if None, selects automatically)
            
        Returns:
            Response as string or dictionary with memory insights
        """
        if not query.strip():
            return "Query cannot be empty."
            
        # Generate session ID if not provided
        if session_id is None:
            session_id = f"session_{int(time.time())}"
        
        # Get intelligent context with token awareness
        context_string, context_stats = self.enhanced_memory.get_context(session_id)
        
        # Show context stats for debugging
        if context_stats.total_interactions > 0:
            print(f"+ Context: {context_stats.estimated_tokens} tokens, {context_stats.total_interactions} interactions")
            if context_stats.summarized_interactions > 0:
                print(f"  - {context_stats.summarized_interactions} summarized, {context_stats.raw_interactions} recent")
        
        # Process with enhanced architecture or basic mode
        if self.enhanced_processing:
            response = self._process_with_enhanced_memory(query, session_id, context_string, tool_name)
        else:
            response = self._process_basic_with_enhanced_memory(query, session_id, context_string, tool_name)
        
        # Extract response text for storage
        response_text = response
        if isinstance(response, dict):
            response_text = response.get("response", str(response))
        
        # Store interaction with intelligent management
        storage_result = self.enhanced_memory.store_interaction(session_id, query, response_text)
        
        # Show storage insights
        if storage_result.get("needs_summarization"):
            print(f"+ Conversation summarized ({storage_result['summarization']['interactions_count']} interactions)")
        
        # Add memory insights to response if it's a dict
        if isinstance(response, dict):
            response["memory_insights"] = {
                "context_stats": context_stats.__dict__,
                "storage_result": storage_result,
                "session_stats": storage_result.get("session_stats", {})
            }
        
        return response
    
    def _process_with_enhanced_memory(
        self,
        query: str,
        session_id: str,
        context_string: str,
        tool_name: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Process query using enhanced architecture with intelligent memory
        """
        try:
            # Step 1: Analyze query
            available_tools = list(self.tools.keys())
            analysis = self.analyzer.analyze_query(
                query, 
                available_tools=available_tools, 
                tools_registry=self.tools
            )
            print(f"+ Query analysis: {analysis.complexity.value} complexity, {analysis.strategy.value} strategy")
            
            # Step 2: Enhanced memory context (already retrieved)
            memory_context = context_string
            
            # Add Titans enhancement if available
            if self.titans_memory_enabled and self.titans_adapter:
                try:
                    enhancement = self.titans_adapter.enhance_query_processing(query, session_id)
                    titans_context = enhancement.get("enhanced_context", "")
                    if titans_context:
                        memory_context = f"{memory_context}\n\n{titans_context}"
                        print(f"+ Enhanced with {len(enhancement.get('relevant_memories', []))} Titans memories")
                except Exception as e:
                    print(f"- Error enhancing with Titans memory: {e}")
            
            # Step 3: Execute using orchestrator
            system_message = self.get_system_message()
            execution_result = self.orchestrator.execute(
                analysis=analysis,
                tools=self.tools,
                llm=self.llm,
                memory_context=memory_context,
                session_id=session_id,
                query=query,
                system_message=system_message,
                config=self.config
            )
            
            # Step 4: Synthesize response
            final_response = self.synthesizer.synthesize_response(
                query=query,
                analysis=analysis,
                execution_result=execution_result,
                llm=self.llm,
                memory_context=memory_context,
                system_message=system_message
            )
            
            # Store in Titans memory if enabled
            if self.titans_memory_enabled and self.titans_adapter:
                try:
                    response_text = final_response.get("response", str(final_response))
                    self.titans_adapter.store_response(query, response_text, session_id)
                except Exception as e:
                    print(f"Warning: Error storing in Titans memory: {e}")
            
            return final_response
            
        except Exception as e:
            print(f"Error in enhanced processing: {e}")
            # Fallback to basic processing
            return self._process_basic_with_enhanced_memory(query, session_id, context_string, tool_name)
    
    def _process_basic_with_enhanced_memory(
        self,
        query: str,
        session_id: str,
        context_string: str,
        tool_name: Optional[str] = None
    ) -> str:
        """
        Basic processing with enhanced memory management
        """
        system_message = self.get_system_message()
        
        # Intelligently include context
        if context_string.strip():
            system_content = f"{system_message}\n\nConversation context:\n{context_string}"
        else:
            system_content = system_message
            
        prompt = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": query}
        ]
        
        response = self.llm.chat(prompt)
        return response
    
    def get_memory_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive memory insights including enhanced memory stats
        """
        # Get base insights from parent
        base_insights = super().get_memory_insights()
        
        # Add enhanced memory insights
        enhanced_insights = self.enhanced_memory.get_memory_insights()
        
        return {
            **base_insights,
            "enhanced_memory": enhanced_insights
        }
    
    def cleanup_old_sessions(self, hours_threshold: Optional[int] = None) -> Dict[str, Any]:
        """
        Clean up old sessions to optimize memory usage
        
        Args:
            hours_threshold: Hours after which to clean sessions
            
        Returns:
            Cleanup results
        """
        return self.enhanced_memory.cleanup_old_sessions(hours_threshold)
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session statistics
        """
        return self.enhanced_memory.get_session_stats(session_id)
    
    def configure_memory(self, **kwargs) -> None:
        """
        Configure memory settings dynamically
        
        Available options:
        - max_context_tokens: Maximum tokens for context
        - summarization_threshold: When to start summarizing
        - session_timeout_hours: Auto-cleanup threshold
        """
        if "max_context_tokens" in kwargs:
            self.enhanced_memory.config.max_context_tokens = max(500, min(8000, int(kwargs["max_context_tokens"])))
            print(f"+ Updated max context tokens to {self.enhanced_memory.config.max_context_tokens}")
        
        if "summarization_threshold" in kwargs:
            self.enhanced_memory.config.summarization_threshold = max(5, min(50, int(kwargs["summarization_threshold"])))
            print(f"+ Updated summarization threshold to {self.enhanced_memory.config.summarization_threshold}")
        
        if "session_timeout_hours" in kwargs:
            self.enhanced_memory.config.session_timeout_hours = max(1, min(168, int(kwargs["session_timeout_hours"])))
            print(f"+ Updated session timeout to {self.enhanced_memory.config.session_timeout_hours} hours")
    
    def show_memory_status(self, session_id: Optional[str] = None) -> None:
        """
        Show current memory status and recommendations
        
        Args:
            session_id: Optional session to show specific stats for
        """
        insights = self.get_memory_insights()
        
        print("\n" + "="*50)
        print("MEMORY STATUS")
        print("="*50)
        
        # Overall stats
        overall = insights["enhanced_memory"]["overall"]
        print(f"Total Sessions: {overall['total_sessions']}")
        print(f"Total Interactions: {overall['total_interactions']}")
        print(f"Total Tokens Used: {overall['total_tokens']:,}")
        print(f"Avg Tokens/Interaction: {overall['avg_tokens_per_interaction']}")
        
        # Recent activity
        recent = insights["enhanced_memory"]["recent_24h"]
        print(f"\nRecent Activity (24h):")
        print(f"  Active Sessions: {recent['active_sessions']}")
        print(f"  Interactions: {recent['interactions']}")
        print(f"  Tokens Used: {recent['tokens_used']:,}")
        
        # Configuration
        config = insights["enhanced_memory"]["configuration"]
        print(f"\nConfiguration:")
        print(f"  Max Context Tokens: {config['max_context_tokens']}")
        print(f"  Summarization Threshold: {config['summarization_threshold']}")
        print(f"  Session Timeout: {config['session_timeout_hours']}h")
        
        # Session-specific stats
        if session_id:
            session_stats = self.get_session_stats(session_id)
            if session_stats.get("exists"):
                print(f"\nSession '{session_id}' Stats:")
                print(f"  Interactions: {session_stats['interaction_count']}")
                print(f"  Tokens Used: {session_stats['total_tokens']:,}")
                print(f"  Summarized: {session_stats['summarized_interactions']}")
                print(f"  Age: {session_stats['session_age_hours']:.1f}h")
                print(f"  Est. Cost: ${session_stats['estimated_cost']:.4f}")
        
        print("="*50)
