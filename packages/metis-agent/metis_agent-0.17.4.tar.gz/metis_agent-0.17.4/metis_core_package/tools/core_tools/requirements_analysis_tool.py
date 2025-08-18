"""
Requirements Analysis Tool for Metis Agent

This tool analyzes project requirements, detects ambiguities, and provides structured
analysis that can be used by the agent to generate dynamic clarifying questions.
Follows tool rules: stateless, no LLM dependencies, pure function behavior.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ..base import BaseTool


class RequirementsAnalysisTool(BaseTool):
    """
    Stateless tool for analyzing project requirements and detecting ambiguities.
    The agent uses this analysis to generate dynamic clarifying questions.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "RequirementsAnalysisTool"
        self.description = "Analyzes project requirements, detects ambiguities, and provides structured analysis for dynamic question generation"
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool schema for the agent."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_request": {
                            "type": "string",
                            "description": "The user's natural language project request"
                        },
                        "analysis_depth": {
                            "type": "string",
                            "enum": ["basic", "detailed", "comprehensive"],
                            "default": "detailed",
                            "description": "Depth of analysis to perform"
                        }
                    },
                    "required": ["project_request"]
                }
            }
        }
    
    def execute(self, project_request: str, analysis_depth: str = "detailed", **kwargs) -> Dict[str, Any]:
        """
        Analyze project requirements and detect areas needing clarification.
        
        Args:
            project_request: The user's natural language request
            analysis_depth: Level of analysis (basic, detailed, comprehensive)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with analysis results that the agent can use to generate questions
        """
        try:
            print(f"[REQUIREMENTS ANALYSIS] Analyzing: {project_request}")
            
            # Step 1: Basic text analysis
            text_analysis = self._analyze_text_structure(project_request)
            
            # Step 2: Detect project type and domain
            project_classification = self._classify_project_type(project_request)
            
            # Step 3: Identify explicit requirements
            explicit_requirements = self._extract_explicit_requirements(project_request)
            
            # Step 4: Detect ambiguities and missing information
            ambiguities = self._detect_ambiguities(project_request, project_classification)
            
            # Step 5: Assess completeness
            completeness_score = self._assess_completeness(explicit_requirements, project_classification)
            
            # Step 6: Generate structured analysis for the agent
            structured_analysis = self._create_structured_analysis(
                project_request, text_analysis, project_classification, 
                explicit_requirements, ambiguities, completeness_score
            )
            
            # Step 7: Provide question generation guidance
            question_guidance = self._generate_question_guidance(
                project_classification, ambiguities, completeness_score
            )
            
            return {
                "success": True,
                "analysis": structured_analysis,
                "questions": question_guidance,
                "structured_requirements": explicit_requirements,
                "completeness_score": completeness_score,
                "ambiguities_detected": len(ambiguities),
                "project_type": project_classification["primary_type"],
                "confidence": project_classification["confidence"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Requirements analysis failed: {str(e)}",
                "analysis": {},
                "questions": [],
                "structured_requirements": {},
                "completeness_score": 0.0
            }
    
    def _analyze_text_structure(self, text: str) -> Dict[str, Any]:
        """Analyze the basic structure and characteristics of the text."""
        words = text.split()
        sentences = text.split('.')
        
        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "has_technical_terms": self._contains_technical_terms(text),
            "specificity_level": self._assess_specificity(text),
            "contains_constraints": self._contains_constraints(text),
            "mentions_technologies": self._extract_mentioned_technologies(text)
        }
    
    def _classify_project_type(self, text: str) -> Dict[str, Any]:
        """Classify the project type based on keywords and context."""
        text_lower = text.lower()
        
        # Project type patterns with confidence scoring
        type_patterns = {
            "web_application": {
                "keywords": ["web app", "website", "web application", "web service", "webapp", "web", "browser"],
                "frameworks": ["flask", "django", "fastapi", "react", "vue", "angular"],
                "indicators": ["html", "css", "javascript", "frontend", "backend", "server"]
            },
            "api_service": {
                "keywords": ["api", "rest api", "web api", "microservice", "service", "endpoint"],
                "frameworks": ["fastapi", "flask", "django rest", "express"],
                "indicators": ["json", "http", "rest", "graphql", "swagger"]
            },
            "cli_tool": {
                "keywords": ["cli", "command line", "terminal", "console", "command"],
                "frameworks": ["click", "argparse", "typer"],
                "indicators": ["arguments", "flags", "options", "terminal"]
            },
            "desktop_application": {
                "keywords": ["desktop", "gui", "window", "application"],
                "frameworks": ["tkinter", "pyqt", "kivy", "electron"],
                "indicators": ["interface", "window", "button", "menu"]
            },
            "data_processing": {
                "keywords": ["data", "analysis", "processing", "etl", "pipeline"],
                "frameworks": ["pandas", "numpy", "spark", "airflow"],
                "indicators": ["csv", "database", "transform", "analyze"]
            },
            "machine_learning": {
                "keywords": ["ml", "machine learning", "ai", "model", "prediction"],
                "frameworks": ["tensorflow", "pytorch", "scikit-learn", "keras"],
                "indicators": ["training", "dataset", "algorithm", "neural"]
            }
        }
        
        # Calculate confidence scores for each type
        type_scores = {}
        for project_type, patterns in type_patterns.items():
            score = 0.0
            
            # Check keywords
            for keyword in patterns["keywords"]:
                if keyword in text_lower:
                    score += 0.3
            
            # Check frameworks
            for framework in patterns["frameworks"]:
                if framework in text_lower:
                    score += 0.4
            
            # Check indicators
            for indicator in patterns["indicators"]:
                if indicator in text_lower:
                    score += 0.1
            
            type_scores[project_type] = min(score, 1.0)
        
        # Find the highest scoring type
        if type_scores:
            primary_type = max(type_scores, key=type_scores.get)
            confidence = type_scores[primary_type]
        else:
            primary_type = "general_application"
            confidence = 0.1
        
        return {
            "primary_type": primary_type,
            "confidence": confidence,
            "all_scores": type_scores,
            "secondary_types": [t for t, s in type_scores.items() if s > 0.2 and t != primary_type]
        }
    
    def _extract_explicit_requirements(self, text: str) -> Dict[str, Any]:
        """Extract explicitly mentioned requirements from the text."""
        requirements = {
            "functional": [],
            "technical": [],
            "constraints": [],
            "features": []
        }
        
        # Look for functional requirements
        functional_patterns = [
            r"should (.*?)(?:\.|$)",
            r"need to (.*?)(?:\.|$)", 
            r"must (.*?)(?:\.|$)",
            r"will (.*?)(?:\.|$)"
        ]
        
        for pattern in functional_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            requirements["functional"].extend([m.strip() for m in matches])
        
        # Look for technical requirements
        tech_keywords = ["database", "framework", "language", "platform", "technology", "stack"]
        for keyword in tech_keywords:
            if keyword in text.lower():
                # Extract context around technical keywords
                context = self._extract_context_around_keyword(text, keyword)
                if context:
                    requirements["technical"].append(context)
        
        # Look for constraints
        constraint_patterns = [
            r"within (\d+\s*(?:days?|weeks?|months?))",
            r"budget of (.*?)(?:\.|$)",
            r"using only (.*?)(?:\.|$)",
            r"without (.*?)(?:\.|$)"
        ]
        
        for pattern in constraint_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            requirements["constraints"].extend([m.strip() for m in matches])
        
        # Extract mentioned features
        feature_keywords = ["login", "authentication", "dashboard", "admin", "search", "filter", "export", "import"]
        for keyword in feature_keywords:
            if keyword in text.lower():
                requirements["features"].append(keyword)
        
        return requirements
    
    def _detect_ambiguities(self, text: str, classification: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect ambiguous or missing information that needs clarification."""
        ambiguities = []
        
        project_type = classification["primary_type"]
        
        # Common ambiguities for all project types
        if not self._mentions_technology_stack(text):
            ambiguities.append({
                "category": "technology",
                "issue": "No specific technology stack mentioned",
                "importance": "high",
                "question_hint": "What programming language and framework would you prefer?"
            })
        
        if not self._mentions_data_storage(text):
            ambiguities.append({
                "category": "data",
                "issue": "Data storage requirements unclear",
                "importance": "medium",
                "question_hint": "Will you need to store data? What type of database?"
            })
        
        # Project-type specific ambiguities
        if project_type == "web_application":
            if not self._mentions_authentication(text):
                ambiguities.append({
                    "category": "authentication",
                    "issue": "User authentication not specified",
                    "importance": "high",
                    "question_hint": "Do you need user registration and login functionality?"
                })
            
            if not self._mentions_ui_framework(text):
                ambiguities.append({
                    "category": "ui",
                    "issue": "UI framework not specified",
                    "importance": "medium",
                    "question_hint": "What UI framework or styling approach would you prefer?"
                })
        
        elif project_type == "api_service":
            if not self._mentions_api_type(text):
                ambiguities.append({
                    "category": "api_type",
                    "issue": "API type not specified",
                    "importance": "high",
                    "question_hint": "What type of API? (REST, GraphQL, etc.)"
                })
        
        elif project_type == "cli_tool":
            if not self._mentions_commands(text):
                ambiguities.append({
                    "category": "commands",
                    "issue": "Specific commands not defined",
                    "importance": "high",
                    "question_hint": "What commands should the CLI tool support?"
                })
        
        return ambiguities
    
    def _assess_completeness(self, requirements: Dict[str, Any], classification: Dict[str, Any]) -> float:
        """Assess how complete the requirements are (0.0 to 1.0)."""
        score = 0.0
        
        # Base score from explicit requirements
        if requirements["functional"]:
            score += 0.3
        if requirements["technical"]:
            score += 0.2
        if requirements["features"]:
            score += 0.2
        
        # Bonus for high confidence classification
        if classification["confidence"] > 0.7:
            score += 0.2
        
        # Penalty for vague requests
        if len(requirements["functional"]) == 0 and len(requirements["features"]) == 0:
            score -= 0.3
        
        return max(0.0, min(1.0, score))
    
    def _create_structured_analysis(self, request: str, text_analysis: Dict, 
                                  classification: Dict, requirements: Dict, 
                                  ambiguities: List, completeness: float) -> Dict[str, Any]:
        """Create a structured analysis for the agent to use."""
        return {
            "original_request": request,
            "analysis_timestamp": datetime.now().isoformat(),
            "text_characteristics": text_analysis,
            "project_classification": classification,
            "explicit_requirements": requirements,
            "ambiguities": ambiguities,
            "completeness_assessment": {
                "score": completeness,
                "level": "high" if completeness > 0.7 else "medium" if completeness > 0.4 else "low",
                "missing_areas": [amb["category"] for amb in ambiguities if amb["importance"] == "high"]
            },
            "recommendation": self._generate_recommendation(completeness, len(ambiguities))
        }
    
    def _generate_question_guidance(self, classification: Dict, ambiguities: List, completeness: float) -> List[Dict[str, Any]]:
        """Generate guidance for the agent to create dynamic questions."""
        guidance = []
        
        # Add guidance based on ambiguities
        for ambiguity in ambiguities:
            guidance.append({
                "category": ambiguity["category"],
                "priority": ambiguity["importance"],
                "question_hint": ambiguity["question_hint"],
                "context": f"Project type: {classification['primary_type']}"
            })
        
        # Add general guidance based on completeness
        if completeness < 0.5:
            guidance.append({
                "category": "general",
                "priority": "high",
                "question_hint": "Can you provide more details about what the application should do?",
                "context": "Low completeness score - need more functional requirements"
            })
        
        return guidance
    
    def _generate_recommendation(self, completeness: float, ambiguity_count: int) -> str:
        """Generate a recommendation for next steps."""
        if completeness > 0.8 and ambiguity_count == 0:
            return "Requirements are clear and complete. Proceed with implementation."
        elif completeness > 0.6:
            return f"Requirements are mostly clear. Consider asking {ambiguity_count} clarifying questions."
        else:
            return f"Requirements need clarification. Recommend asking {ambiguity_count} questions to gather more details."
    
    # Helper methods for text analysis
    def _contains_technical_terms(self, text: str) -> bool:
        tech_terms = ["api", "database", "framework", "library", "server", "client", "frontend", "backend"]
        return any(term in text.lower() for term in tech_terms)
    
    def _assess_specificity(self, text: str) -> str:
        if len(text.split()) < 5:
            return "very_low"
        elif len(text.split()) < 15:
            return "low"
        elif len(text.split()) < 30:
            return "medium"
        else:
            return "high"
    
    def _contains_constraints(self, text: str) -> bool:
        constraint_words = ["within", "budget", "deadline", "only", "without", "must", "cannot"]
        return any(word in text.lower() for word in constraint_words)
    
    def _extract_mentioned_technologies(self, text: str) -> List[str]:
        technologies = ["python", "javascript", "react", "vue", "angular", "flask", "django", "fastapi", "node", "express"]
        return [tech for tech in technologies if tech in text.lower()]
    
    def _mentions_technology_stack(self, text: str) -> bool:
        return len(self._extract_mentioned_technologies(text)) > 0
    
    def _mentions_data_storage(self, text: str) -> bool:
        storage_terms = ["database", "storage", "data", "sqlite", "postgresql", "mongodb", "mysql"]
        return any(term in text.lower() for term in storage_terms)
    
    def _mentions_authentication(self, text: str) -> bool:
        auth_terms = ["login", "authentication", "register", "user", "account", "auth"]
        return any(term in text.lower() for term in auth_terms)
    
    def _mentions_ui_framework(self, text: str) -> bool:
        ui_terms = ["bootstrap", "tailwind", "css", "styling", "theme", "ui", "interface"]
        return any(term in text.lower() for term in ui_terms)
    
    def _mentions_api_type(self, text: str) -> bool:
        api_terms = ["rest", "graphql", "soap", "grpc", "json", "xml"]
        return any(term in text.lower() for term in api_terms)
    
    def _mentions_commands(self, text: str) -> bool:
        command_terms = ["command", "option", "flag", "argument", "subcommand"]
        return any(term in text.lower() for term in command_terms)
    
    def _extract_context_around_keyword(self, text: str, keyword: str) -> Optional[str]:
        """Extract context around a keyword."""
        words = text.split()
        for i, word in enumerate(words):
            if keyword.lower() in word.lower():
                start = max(0, i - 3)
                end = min(len(words), i + 4)
                return " ".join(words[start:end])
        return None
    
    def can_handle(self, task: str) -> bool:
        """Check if this tool can handle the given task."""
        task_lower = task.lower()
        keywords = ["analyze", "requirements", "clarify", "ambiguity", "specification"]
        return any(keyword in task_lower for keyword in keywords)


# Register the tool
def get_tool():
    """Get an instance of the RequirementsAnalysisTool."""
    return RequirementsAnalysisTool()
