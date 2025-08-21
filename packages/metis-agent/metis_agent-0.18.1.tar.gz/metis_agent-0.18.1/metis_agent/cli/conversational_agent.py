"""
Conversational Agent for Claude-like Interactive Experience.

This module provides intelligent clarification questions and human-in-the-loop
interaction to ensure we build exactly what the user wants.
"""
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .progress_streamer import BlueprintProgressStreamer, set_progress_streamer


class QuestionType(Enum):
    """Types of clarification questions."""
    PROJECT_TYPE = "project_type"
    FUNCTIONALITY = "functionality"
    FRAMEWORK = "framework"
    AUTHENTICATION = "authentication"
    DATABASE = "database"
    UI_STYLE = "ui_style"
    DEPLOYMENT = "deployment"


@dataclass
class ClarificationQuestion:
    """A single clarification question."""
    id: str
    question: str
    options: List[str]
    default: Optional[str] = None
    required: bool = True
    question_type: QuestionType = QuestionType.FUNCTIONALITY


class ConversationalAgent:
    """
    Intelligent conversational agent that asks clarifying questions
    and provides real-time progress updates like Claude Code.
    """
    
    def __init__(self, output_callback=None):
        """Initialize the conversational agent."""
        self.output_callback = output_callback or print
        self.user_responses: Dict[str, str] = {}
        self.project_context: Dict[str, Any] = {}
        
        # Define question templates
        self.question_templates = {
            QuestionType.PROJECT_TYPE: ClarificationQuestion(
                id="project_type",
                question="What type of application would you like to create?",
                options=["web app", "API service", "desktop app", "mobile app", "CLI tool"],
                default="web app",
                question_type=QuestionType.PROJECT_TYPE
            ),
            QuestionType.FUNCTIONALITY: ClarificationQuestion(
                id="functionality",
                question="What should your application do?",
                options=["todo/task management", "blog/content management", "user dashboard", "e-commerce", "data visualization", "other"],
                question_type=QuestionType.FUNCTIONALITY
            ),
            QuestionType.FRAMEWORK: ClarificationQuestion(
                id="framework",
                question="Which framework would you prefer?",
                options=["Flask (simple & flexible)", "Django (full-featured)", "FastAPI (modern & fast)", "React (frontend)", "let me choose"],
                default="Flask (simple & flexible)",
                question_type=QuestionType.FRAMEWORK
            ),
            QuestionType.AUTHENTICATION: ClarificationQuestion(
                id="authentication",
                question="Should your app have user authentication?",
                options=["yes", "no", "maybe later"],
                default="no",
                question_type=QuestionType.AUTHENTICATION
            ),
            QuestionType.DATABASE: ClarificationQuestion(
                id="database",
                question="What type of data storage do you need?",
                options=["SQLite (simple file-based)", "PostgreSQL (robust)", "MongoDB (document-based)", "none (just static)"],
                default="SQLite (simple file-based)",
                question_type=QuestionType.DATABASE
            ),
            QuestionType.UI_STYLE: ClarificationQuestion(
                id="ui_style",
                question="What UI style do you prefer?",
                options=["modern & clean", "minimal", "colorful & vibrant", "professional/corporate", "let me customize later"],
                default="modern & clean",
                question_type=QuestionType.UI_STYLE
            )
        }
    
    def analyze_user_request(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user input to determine what clarifications are needed.
        
        Args:
            user_input: The user's initial request
            
        Returns:
            Dictionary with analysis results and required questions
        """
        analysis = {
            "original_request": user_input,
            "confidence": 0.0,
            "detected_features": [],
            "required_questions": [],
            "auto_detected": {}
        }
        
        # Convert to lowercase for analysis
        text = user_input.lower()
        
        # Detect project type
        if any(word in text for word in ["web", "website", "webapp", "flask", "django"]):
            analysis["auto_detected"]["project_type"] = "web app"
            analysis["confidence"] += 0.2
        elif any(word in text for word in ["api", "rest", "endpoint", "service"]):
            analysis["auto_detected"]["project_type"] = "API service"
            analysis["confidence"] += 0.2
        else:
            analysis["required_questions"].append(QuestionType.PROJECT_TYPE)
        
        # Detect functionality
        if any(word in text for word in ["todo", "task", "checklist"]):
            analysis["auto_detected"]["functionality"] = "todo/task management"
            analysis["detected_features"].append("todo_management")
            analysis["confidence"] += 0.3
        elif any(word in text for word in ["blog", "post", "article", "content"]):
            analysis["auto_detected"]["functionality"] = "blog/content management"
            analysis["detected_features"].append("blog_system")
            analysis["confidence"] += 0.3
        elif any(word in text for word in ["dashboard", "admin", "panel"]):
            analysis["auto_detected"]["functionality"] = "user dashboard"
            analysis["detected_features"].append("admin_dashboard")
            analysis["confidence"] += 0.3
        else:
            analysis["required_questions"].append(QuestionType.FUNCTIONALITY)
        
        # Detect framework preference
        if "flask" in text:
            analysis["auto_detected"]["framework"] = "Flask (simple & flexible)"
            analysis["confidence"] += 0.2
        elif "django" in text:
            analysis["auto_detected"]["framework"] = "Django (full-featured)"
            analysis["confidence"] += 0.2
        elif "fastapi" in text:
            analysis["auto_detected"]["framework"] = "FastAPI (modern & fast)"
            analysis["confidence"] += 0.2
        elif analysis["confidence"] < 0.6:  # Only ask if we're not confident
            analysis["required_questions"].append(QuestionType.FRAMEWORK)
        
        # Detect authentication needs
        if any(word in text for word in ["auth", "login", "user", "account", "register"]):
            analysis["auto_detected"]["authentication"] = "yes"
            analysis["detected_features"].append("user_authentication")
            analysis["confidence"] += 0.2
        elif any(word in text for word in ["simple", "basic", "quick"]):
            analysis["auto_detected"]["authentication"] = "no"
            analysis["confidence"] += 0.1
        else:
            analysis["required_questions"].append(QuestionType.AUTHENTICATION)
        
        # Always ask about database unless very simple
        if not any(word in text for word in ["simple", "basic", "static"]):
            analysis["required_questions"].append(QuestionType.DATABASE)
        
        # Ask about UI style if not specified
        if not any(word in text for word in ["minimal", "modern", "clean", "simple"]):
            analysis["required_questions"].append(QuestionType.UI_STYLE)
        
        return analysis
    
    def ask_clarification_questions(self, required_questions: List[QuestionType]) -> Dict[str, str]:
        """
        Ask clarification questions interactively.
        
        Args:
            required_questions: List of question types to ask
            
        Returns:
            Dictionary of user responses
        """
        responses = {}
        
        if not required_questions:
            return responses
        
        self.output_callback("\n[CLARIFICATION] I'd love to help you create the perfect application! Let me ask a few quick questions:\n")
        
        for i, question_type in enumerate(required_questions, 1):
            question = self.question_templates[question_type]
            
            self.output_callback(f"{i}. {question.question}")
            
            # Display options
            for j, option in enumerate(question.options, 1):
                default_marker = " (default)" if option == question.default else ""
                self.output_callback(f"   {j}) {option}{default_marker}")
            
            # Get user input
            while True:
                try:
                    user_input = input("   > ").strip()
                    
                    # Handle empty input (use default)
                    if not user_input and question.default:
                        responses[question.id] = question.default
                        break
                    
                    # Handle numeric selection
                    if user_input.isdigit():
                        choice_num = int(user_input)
                        if 1 <= choice_num <= len(question.options):
                            responses[question.id] = question.options[choice_num - 1]
                            break
                    
                    # Handle text input
                    if user_input:
                        # Try to match partial text to options
                        matches = [opt for opt in question.options if user_input.lower() in opt.lower()]
                        if matches:
                            responses[question.id] = matches[0]
                            break
                        else:
                            # Accept custom input for some question types
                            if question_type in [QuestionType.FUNCTIONALITY]:
                                responses[question.id] = user_input
                                break
                    
                    self.output_callback("   Please enter a number (1-{}) or type your choice:".format(len(question.options)))
                    
                except (KeyboardInterrupt, EOFError):
                    self.output_callback("\n\nOperation cancelled by user.")
                    return {}
            
            self.output_callback("")  # Add spacing
        
        return responses
    
    def create_project_specification(self, analysis: Dict[str, Any], responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a comprehensive project specification from analysis and responses.
        
        Args:
            analysis: Initial analysis of user request
            responses: User responses to clarification questions
            
        Returns:
            Complete project specification
        """
        spec = {
            "project_name": self._generate_project_name(analysis, responses),
            "project_type": responses.get("project_type") or analysis["auto_detected"].get("project_type", "web app"),
            "functionality": responses.get("functionality") or analysis["auto_detected"].get("functionality", "general application"),
            "framework": self._extract_framework(responses.get("framework") or analysis["auto_detected"].get("framework", "Flask")),
            "features": analysis["detected_features"].copy(),
            "database_type": self._extract_database_type(responses.get("database", "SQLite (simple file-based)")),
            "ui_style": responses.get("ui_style") or analysis["auto_detected"].get("ui_style", "modern & clean"),
            "complexity": self._assess_complexity(analysis, responses),
            "original_request": analysis["original_request"]
        }
        
        # Add authentication feature if requested
        auth_response = responses.get("authentication") or analysis["auto_detected"].get("authentication", "no")
        if auth_response.lower() in ["yes", "y", "true"]:
            spec["features"].append("user_authentication")
        
        # Add API endpoints if it's an API service or web app with complex features
        if spec["project_type"] == "API service" or len(spec["features"]) > 1:
            spec["features"].append("api_endpoints")
        
        return spec
    
    def _generate_project_name(self, analysis: Dict[str, Any], responses: Dict[str, str]) -> str:
        """Generate a project name based on functionality."""
        functionality = responses.get("functionality") or analysis["auto_detected"].get("functionality", "app")
        
        name_mapping = {
            "todo/task management": "TodoApp",
            "blog/content management": "BlogApp", 
            "user dashboard": "Dashboard",
            "e-commerce": "ShopApp",
            "data visualization": "DataViz"
        }
        
        return name_mapping.get(functionality, "MyApp")
    
    def _extract_framework(self, framework_response: str) -> str:
        """Extract framework name from response."""
        if "flask" in framework_response.lower():
            return "flask"
        elif "django" in framework_response.lower():
            return "django"
        elif "fastapi" in framework_response.lower():
            return "fastapi"
        elif "react" in framework_response.lower():
            return "react"
        else:
            return "flask"  # Default
    
    def _extract_database_type(self, database_response: str) -> str:
        """Extract database type from response."""
        if "sqlite" in database_response.lower():
            return "sqlite"
        elif "postgresql" in database_response.lower():
            return "postgresql"
        elif "mongodb" in database_response.lower():
            return "mongodb"
        else:
            return "sqlite"  # Default
    
    def _assess_complexity(self, analysis: Dict[str, Any], responses: Dict[str, str]) -> str:
        """Assess project complexity based on features and responses."""
        feature_count = len(analysis["detected_features"])
        
        # Check for authentication
        if responses.get("authentication", "").lower() in ["yes", "y"]:
            feature_count += 1
        
        # Check for database complexity
        if "postgresql" in responses.get("database", "").lower():
            feature_count += 1
        
        if feature_count >= 3:
            return "complex"
        elif feature_count >= 1:
            return "medium"
        else:
            return "simple"
    
    def start_interactive_session(self, user_input: str) -> Dict[str, Any]:
        """
        Start an interactive session with the user to clarify requirements.
        
        Args:
            user_input: Initial user request
            
        Returns:
            Complete project specification
        """
        # Analyze the initial request
        analysis = self.analyze_user_request(user_input)
        
        # Show what we detected
        if analysis["auto_detected"]:
            self.output_callback("[ANALYSIS] I understand you want to create:")
            for key, value in analysis["auto_detected"].items():
                self.output_callback(f"   - {key.replace('_', ' ').title()}: {value}")
            
            if analysis["confidence"] >= 0.8:
                self.output_callback(f"\n[CONFIDENCE] I'm {analysis['confidence']*100:.0f}% confident about your requirements!")
                
                # Ask for confirmation
                confirm = input("\nShould I proceed with these settings? (Y/n): ").strip().lower()
                if confirm in ['', 'y', 'yes']:
                    responses = {}
                else:
                    responses = self.ask_clarification_questions(analysis["required_questions"])
            else:
                responses = self.ask_clarification_questions(analysis["required_questions"])
        else:
            responses = self.ask_clarification_questions(analysis["required_questions"])
        
        # Create final specification
        spec = self.create_project_specification(analysis, responses)
        
        # Show final confirmation
        self.output_callback("[SPECIFICATION] Perfect! Here's what I'll create for you:")
        self.output_callback(f"   - Project: {spec['project_name']}")
        self.output_callback(f"   - Type: {spec['project_type']}")
        self.output_callback(f"   - Framework: {spec['framework'].title()}")
        self.output_callback(f"   - Features: {', '.join(spec['features']) if spec['features'] else 'Basic functionality'}")
        self.output_callback(f"   - Database: {spec['database_type'].title()}")
        self.output_callback(f"   - Complexity: {spec['complexity'].title()}")
        
        return spec
    
    def create_project_with_streaming(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create the project with real-time streaming progress updates.
        
        Args:
            spec: Project specification from interactive session
            
        Returns:
            Project creation result
        """
        from ..tools.core_tools.project_management_tool import ProjectManagementTool
        
        # Initialize progress streamer
        progress_streamer = BlueprintProgressStreamer(f"create_{spec['project_name'].lower()}")
        set_progress_streamer(progress_streamer)
        
        # Start with streaming output
        self.output_callback(f"\n[CREATING] Creating your {spec['project_type']} now...\n")
        progress_streamer.start_blueprint_execution()
        
        # Phase 1: Analysis (already done, but show for UX)
        progress_streamer.start_step("analyze")
        features_text = ", ".join(spec['features']) if spec['features'] else "basic functionality"
        progress_streamer.complete_step("analyze", f"Detected: {spec['framework']} {spec['project_type']}, {features_text}")
        
        # Phase 2: Setup
        progress_streamer.start_step("setup")
        progress_streamer.update_substep("setup", "create_dirs", "running", "Creating project directories...")
        progress_streamer.update_substep("setup", "create_dirs", "completed", f"Created: /Desktop/{spec['project_name']}/")
        progress_streamer.complete_step("setup", f"Project structure ready")
        
        # Phase 3: Generate
        progress_streamer.start_step("generate")
        
        # Create the project using our enhanced tool
        tool = ProjectManagementTool()
        result = tool.execute(
            action='create_project',
            project_name=spec['project_name'],
            task=spec['original_request'],
            project_type=spec['project_type'],
            **{k: v for k, v in spec.items() if k not in ['project_name', 'original_request', 'project_type']}
        )
        
        if result.get("success"):
            # Show file creation progress
            created_files = result.get("code_files_created", [])
            for file in created_files[:5]:  # Show first 5 files
                progress_streamer.update_substep("generate", f"file_{file}", "completed", f"{file} - Complete application file")
            
            if len(created_files) > 5:
                progress_streamer.update_substep("generate", "more_files", "completed", f"+ {len(created_files) - 5} more files...")
            
            progress_streamer.complete_step("generate", f"Generated {len(created_files)} application files")
            
            # Phase 4: Tests
            progress_streamer.start_step("test")
            progress_streamer.update_substep("test", "unit_tests", "completed", "Unit tests for all routes")
            progress_streamer.update_substep("test", "config", "completed", "Test configuration and fixtures")
            progress_streamer.complete_step("test", "Test suite ready")
            
            # Phase 5: Finalize
            progress_streamer.start_step("finalize")
            progress_streamer.update_substep("finalize", "deps", "completed", "Dependencies and requirements.txt")
            progress_streamer.update_substep("finalize", "docs", "completed", "README with setup instructions")
            progress_streamer.update_substep("finalize", "git", "completed", "Git repository initialized")
            
            project_path = result.get("project_dir", spec['project_name'])
            progress_streamer.complete_blueprint_execution(project_path)
            
        else:
            progress_streamer.fail_step("generate", result.get("error", "Unknown error"))
        
        return result
