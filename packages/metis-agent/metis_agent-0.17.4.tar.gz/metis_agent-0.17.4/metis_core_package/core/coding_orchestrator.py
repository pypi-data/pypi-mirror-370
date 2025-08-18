"""
Enhanced Coding Orchestrator for Metis Agent.

This module provides specialized orchestration for coding tasks with:
- LLM-driven clarification questions
- Comprehensive project planning
- Planning document generation (plan.md, tasks.md, design.md)
- Context-aware code generation coordination
"""
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from .models import QueryAnalysis, ExecutionResult, QueryComplexity, ExecutionStrategy
from .llm_interface import get_llm
from .smart_orchestrator import SmartOrchestrator
from ..tools.registry import get_tool


class CodingQuestion:
    """Represents a clarification question for coding tasks."""
    
    def __init__(self, question: str, category: str, priority: int = 1, 
                 follow_up: bool = False, context: str = ""):
        self.question = question
        self.category = category  # requirements, tech_stack, architecture, constraints, deployment
        self.priority = priority  # 1=high, 2=medium, 3=low
        self.follow_up = follow_up
        self.context = context
        self.answer = None


class CodingAnalysis:
    """Enhanced analysis for coding tasks."""
    
    def __init__(self, query: str, complexity: QueryComplexity, 
                 project_type: str = None, missing_context: List[str] = None,
                 questions: List[CodingQuestion] = None, confidence: float = 0.8):
        self.query = query
        self.complexity = complexity
        self.project_type = project_type or "unknown"
        self.missing_context = missing_context or []
        self.questions = questions or []
        self.confidence = confidence
        self.requires_clarification = len(self.questions) > 0


class EnhancedRequirements:
    """Comprehensive requirements after clarification."""
    
    def __init__(self, original_query: str, clarified_requirements: Dict[str, Any],
                 project_context: Dict[str, Any], technical_specs: Dict[str, Any]):
        self.original_query = original_query
        self.clarified_requirements = clarified_requirements
        self.project_context = project_context
        self.technical_specs = technical_specs
        self.timestamp = datetime.now().isoformat()


class ProjectPlan:
    """Comprehensive project plan with all planning documents."""
    
    def __init__(self, requirements: EnhancedRequirements):
        self.requirements = requirements
        self.plan_content = ""
        self.tasks_content = ""
        self.design_content = ""
        self.file_structure = {}
        self.estimated_timeline = ""
        self.complexity_assessment = ""


class IntelligentClarificationEngine:
    """Uses LLM reasoning to generate contextual clarifying questions."""
    
    def __init__(self):
        self.question_categories = {
            'requirements': "Core functionality and features",
            'tech_stack': "Technology choices and preferences", 
            'architecture': "System design and patterns",
            'constraints': "Performance, security, and limitations",
            'deployment': "Hosting and distribution strategy"
        }
    
    def generate_clarification_questions(self, query: str, context: Dict = None) -> List[CodingQuestion]:
        """Generate intelligent clarifying questions using LLM analysis."""
        
        system_prompt = f"""You are an expert software architect and project planner. Your job is to analyze coding requests and identify what clarifying questions need to be asked to create the best possible solution.

Analyze the user's request and determine what critical information is missing or ambiguous. Generate specific, actionable questions that will help create a comprehensive project plan.

QUESTION CATEGORIES:
- requirements: Core functionality, features, user needs
- tech_stack: Programming languages, frameworks, libraries, tools
- architecture: Design patterns, system structure, scalability
- constraints: Performance requirements, security needs, limitations, budget
- deployment: Hosting, distribution, environment, CI/CD

GUIDELINES:
- Ask 2-5 questions maximum (prioritize the most important)
- Make questions specific and actionable
- Avoid generic questions - tailor to the specific request
- Consider the complexity of the request
- Focus on information that significantly impacts the solution

Respond in JSON format:
{{
  "questions": [
    {{
      "question": "Specific question text",
      "category": "one of the categories above",
      "priority": 1-3 (1=critical, 2=important, 3=nice-to-have),
      "context": "Why this question matters for the solution"
    }}
  ],
  "analysis": {{
    "project_type": "web_app|mobile_app|api|library|tool|game|other",
    "complexity": "simple|moderate|complex|enterprise",
    "missing_critical_info": ["list", "of", "missing", "info"],
    "confidence": 0.0-1.0
  }}
}}"""

        user_prompt = f"""Analyze this coding request and generate clarifying questions:

REQUEST: "{query}"

CONTEXT: {json.dumps(context or {}, indent=2)}

Generate the most important clarifying questions to create an optimal solution."""

        try:
            llm = get_llm()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = llm.chat(messages)
            result = self._parse_llm_response(response)
            
            questions = []
            for q_data in result.get("questions", []):
                question = CodingQuestion(
                    question=q_data.get("question", ""),
                    category=q_data.get("category", "requirements"),
                    priority=q_data.get("priority", 2),
                    context=q_data.get("context", "")
                )
                questions.append(question)
            
            return questions
            
        except Exception as e:
            print(f"Error generating clarification questions: {e}")
            # Fallback to basic questions
            return self._generate_fallback_questions(query)
    
    def process_clarification_responses(self, questions: List[CodingQuestion], 
                                      responses: List[str]) -> EnhancedRequirements:
        """Process user responses and create enhanced requirements."""
        
        # Match responses to questions
        for i, response in enumerate(responses):
            if i < len(questions):
                questions[i].answer = response
        
        # Use LLM to synthesize responses into structured requirements
        system_prompt = """You are an expert requirements analyst. Your job is to take user responses to clarifying questions and synthesize them into a comprehensive, structured requirements specification.

Create a detailed requirements document that captures:
1. Core functionality and features
2. Technical specifications and constraints
3. Architecture and design considerations
4. Deployment and operational requirements

Be specific and actionable. Fill in reasonable defaults for any gaps."""

        qa_pairs = []
        for q in questions:
            if q.answer:
                qa_pairs.append(f"Q: {q.question}\nA: {q.answer}\nCategory: {q.category}")
        
        user_prompt = f"""Original Query: {questions[0].question if questions else "Unknown"}

Question & Answer Pairs:
{chr(10).join(qa_pairs)}

Synthesize these responses into a comprehensive requirements specification in JSON format:
{{
  "clarified_requirements": {{
    "core_features": ["list of main features"],
    "user_stories": ["list of user stories"],
    "functional_requirements": ["detailed functional requirements"]
  }},
  "project_context": {{
    "project_type": "web_app|api|library|tool|etc",
    "target_users": "description of target users",
    "use_cases": ["primary use cases"]
  }},
  "technical_specs": {{
    "programming_language": "primary language",
    "framework": "chosen framework",
    "database": "database choice",
    "architecture_pattern": "architectural approach",
    "deployment_target": "deployment environment",
    "performance_requirements": "performance needs",
    "security_requirements": "security considerations"
  }}
}}"""

        try:
            llm = get_llm()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = llm.chat(messages)
            result = self._parse_llm_response(response)
            
            return EnhancedRequirements(
                original_query=questions[0].question if questions else "Unknown",
                clarified_requirements=result.get("clarified_requirements", {}),
                project_context=result.get("project_context", {}),
                technical_specs=result.get("technical_specs", {})
            )
            
        except Exception as e:
            print(f"Error processing clarification responses: {e}")
            # Return basic requirements
            return self._create_fallback_requirements(questions, responses)
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLM."""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                return {"error": "No JSON found in response"}
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return {"error": f"JSON parse error: {e}"}
    
    def _generate_fallback_questions(self, query: str) -> List[CodingQuestion]:
        """Generate basic fallback questions when LLM fails."""
        questions = []
        
        # Basic questions based on query analysis
        if any(word in query.lower() for word in ['web', 'app', 'website', 'api']):
            questions.append(CodingQuestion(
                "What specific features should this web application have?",
                "requirements", 1, context="Core functionality definition"
            ))
            questions.append(CodingQuestion(
                "What technology stack do you prefer? (React, Vue, FastAPI, Django, etc.)",
                "tech_stack", 1, context="Technology selection impacts architecture"
            ))
        
        if any(word in query.lower() for word in ['create', 'build', 'develop']):
            questions.append(CodingQuestion(
                "Who are the target users and what are their main use cases?",
                "requirements", 2, context="User-centered design"
            ))
        
        return questions[:3]  # Limit to 3 questions
    
    def _create_fallback_requirements(self, questions: List[CodingQuestion], 
                                    responses: List[str]) -> EnhancedRequirements:
        """Create basic requirements when LLM processing fails."""
        clarified_requirements = {}
        project_context = {}
        technical_specs = {}
        
        # Extract basic info from Q&A pairs
        for i, q in enumerate(questions):
            if i < len(responses) and responses[i]:
                if q.category == "requirements":
                    clarified_requirements[f"requirement_{i}"] = responses[i]
                elif q.category == "tech_stack":
                    technical_specs[f"tech_choice_{i}"] = responses[i]
                elif q.category == "architecture":
                    technical_specs[f"architecture_{i}"] = responses[i]
        
        return EnhancedRequirements(
            original_query=questions[0].question if questions else "Unknown",
            clarified_requirements=clarified_requirements,
            project_context=project_context,
            technical_specs=technical_specs
        )


class IntelligentProjectPlanner:
    """Creates comprehensive project plans using LLM reasoning."""
    
    def __init__(self):
        self.planning_templates = {
            'web_app': "Web application development template",
            'api': "REST API development template", 
            'library': "Library/package development template",
            'tool': "CLI tool development template"
        }
    
    def create_project_plan(self, requirements: EnhancedRequirements) -> ProjectPlan:
        """Generate comprehensive project plan with all planning documents."""
        
        plan = ProjectPlan(requirements)
        
        # Generate each planning document
        plan.plan_content = self._generate_plan_md(requirements)
        plan.tasks_content = self._generate_tasks_md(requirements)
        plan.design_content = self._generate_design_md(requirements)
        
        return plan
    
    def _generate_plan_md(self, requirements: EnhancedRequirements) -> str:
        """Generate plan.md content using LLM."""
        
        system_prompt = """You are an expert project manager and software architect. Create a comprehensive project plan document (plan.md) based on the provided requirements.

The plan should include:
1. Project Overview (complexity, timeline, tech stack, architecture)
2. Requirements Summary (clear, actionable requirements)
3. Development Strategy (methodology, phases, approach)
4. Risk Assessment (potential challenges and mitigation)
5. Success Criteria (measurable outcomes)

Make it professional, detailed, and actionable. Use markdown formatting."""

        user_prompt = f"""Create a comprehensive project plan for:

ORIGINAL REQUEST: {requirements.original_query}

REQUIREMENTS:
{json.dumps(requirements.clarified_requirements, indent=2)}

PROJECT CONTEXT:
{json.dumps(requirements.project_context, indent=2)}

TECHNICAL SPECIFICATIONS:
{json.dumps(requirements.technical_specs, indent=2)}

Generate a detailed plan.md document."""

        try:
            llm = get_llm()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            return llm.chat(messages)
            
        except Exception as e:
            print(f"Error generating plan.md: {e}")
            return self._generate_fallback_plan(requirements)
    
    def _generate_tasks_md(self, requirements: EnhancedRequirements) -> str:
        """Generate tasks.md content using LLM."""
        
        system_prompt = """You are an expert project manager. Create a detailed task breakdown document (tasks.md) with specific, actionable tasks organized by development phases.

Include:
1. Task breakdown by phases
2. Checkboxes for each task
3. Effort estimates (hours/days)
4. Task dependencies
5. Acceptance criteria for key tasks

Make tasks specific, measurable, and achievable. Use markdown formatting with checkboxes."""

        user_prompt = f"""Create a detailed task breakdown for:

ORIGINAL REQUEST: {requirements.original_query}

REQUIREMENTS:
{json.dumps(requirements.clarified_requirements, indent=2)}

TECHNICAL SPECIFICATIONS:
{json.dumps(requirements.technical_specs, indent=2)}

Generate a comprehensive tasks.md document with checkboxes and estimates."""

        try:
            llm = get_llm()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            return llm.chat(messages)
            
        except Exception as e:
            print(f"Error generating tasks.md: {e}")
            return self._generate_fallback_tasks(requirements)
    
    def _generate_design_md(self, requirements: EnhancedRequirements) -> str:
        """Generate design.md content using LLM."""
        
        system_prompt = """You are an expert software architect. Create a comprehensive technical design document (design.md) based on the requirements.

Include:
1. Architecture Overview (high-level system design)
2. Technology Decisions (rationale for tech choices)
3. System Components (detailed component breakdown)
4. Data Models (database schema, data structures)
5. API Design (endpoints, contracts if applicable)
6. Security Considerations (security measures)
7. Performance Requirements (optimization strategies)
8. Deployment Architecture (infrastructure strategy)

Make it technical, detailed, and implementation-focused. Use markdown formatting."""

        user_prompt = f"""Create a comprehensive technical design document for:

ORIGINAL REQUEST: {requirements.original_query}

REQUIREMENTS:
{json.dumps(requirements.clarified_requirements, indent=2)}

TECHNICAL SPECIFICATIONS:
{json.dumps(requirements.technical_specs, indent=2)}

Generate a detailed design.md document with technical architecture."""

        try:
            llm = get_llm()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            return llm.chat(messages)
            
        except Exception as e:
            print(f"Error generating design.md: {e}")
            return self._generate_fallback_design(requirements)
    
    def generate_planning_documents(self, project_plan: ProjectPlan, 
                                  output_dir: str = ".") -> Dict[str, str]:
        """Write planning documents to files and return file paths."""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        files_created = {}
        
        # Write plan.md
        plan_file = output_path / "plan.md"
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(project_plan.plan_content)
        files_created['plan'] = str(plan_file)
        
        # Write tasks.md
        tasks_file = output_path / "tasks.md"
        with open(tasks_file, 'w', encoding='utf-8') as f:
            f.write(project_plan.tasks_content)
        files_created['tasks'] = str(tasks_file)
        
        # Write design.md
        design_file = output_path / "design.md"
        with open(design_file, 'w', encoding='utf-8') as f:
            f.write(project_plan.design_content)
        files_created['design'] = str(design_file)
        
        return files_created
    
    def _generate_fallback_plan(self, requirements: EnhancedRequirements) -> str:
        """Generate basic plan.md when LLM fails."""
        return f"""# Project Plan - {requirements.original_query}

## Project Overview
- **Request:** {requirements.original_query}
- **Complexity:** Moderate
- **Estimated Timeline:** 2-4 weeks
- **Status:** Planning Phase

## Requirements Summary
{json.dumps(requirements.clarified_requirements, indent=2)}

## Technical Specifications
{json.dumps(requirements.technical_specs, indent=2)}

## Development Strategy
1. Requirements analysis and planning
2. Architecture design and setup
3. Core functionality implementation
4. Testing and validation
5. Documentation and deployment

## Success Criteria
- All requirements implemented and tested
- Code quality meets standards
- Documentation is complete
- System is deployable
"""
    
    def _generate_fallback_tasks(self, requirements: EnhancedRequirements) -> str:
        """Generate basic tasks.md when LLM fails."""
        return f"""# Project Tasks - {requirements.original_query}

## Phase 1: Setup and Planning
- [ ] Project setup and initialization
- [ ] Development environment configuration
- [ ] Architecture planning and design

## Phase 2: Core Development
- [ ] Implement core functionality
- [ ] Add error handling and validation
- [ ] Create tests for main features

## Phase 3: Integration and Testing
- [ ] Integration testing
- [ ] Performance testing
- [ ] Security review

## Phase 4: Documentation and Deployment
- [ ] Complete documentation
- [ ] Deployment preparation
- [ ] Final testing and validation

## Task Dependencies
Tasks should be completed in order within each phase.

## Effort Estimation
- Phase 1: 1-2 days
- Phase 2: 1-2 weeks  
- Phase 3: 2-3 days
- Phase 4: 1-2 days
"""
    
    def _generate_fallback_design(self, requirements: EnhancedRequirements) -> str:
        """Generate basic design.md when LLM fails."""
        return f"""# Technical Design Document - {requirements.original_query}

## Architecture Overview
This project follows standard software development practices with a modular architecture.

## Technology Decisions
Based on requirements analysis:
{json.dumps(requirements.technical_specs, indent=2)}

## System Components
- Core application logic
- Data management layer
- User interface (if applicable)
- Testing framework
- Documentation system

## Security Considerations
- Input validation and sanitization
- Error handling and logging
- Secure configuration management

## Performance Requirements
- Efficient algorithms and data structures
- Appropriate caching strategies
- Scalable architecture design

## Deployment Architecture
- Development environment setup
- Testing and staging environments
- Production deployment strategy
"""
    
    def generate_planning_documents(self, project_plan: ProjectPlan, output_dir: str = '.') -> Dict[str, str]:
        """Generate and write planning documents to disk in a Metis directory, intelligently updating existing files."""
        from pathlib import Path
        
        # Check if we're already in a Metis directory or need to create one
        base_path = Path(output_dir).resolve()
        if base_path.name == 'Metis':
            # We're already in the Metis directory
            metis_path = base_path
        else:
            # Create a 'Metis' directory for project files
            metis_path = base_path / 'Metis'
        metis_path.mkdir(parents=True, exist_ok=True)
        
        files_created = {}
        
        # Update plan.md
        plan_file = metis_path / 'plan.md'
        updated_plan = self._update_planning_document(plan_file, project_plan.plan_content, 'plan')
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(updated_plan)
        files_created['plan'] = str(plan_file)
        
        # Update tasks.md
        tasks_file = metis_path / 'tasks.md'
        updated_tasks = self._update_planning_document(tasks_file, project_plan.tasks_content, 'tasks')
        with open(tasks_file, 'w', encoding='utf-8') as f:
            f.write(updated_tasks)
        files_created['tasks'] = str(tasks_file)
        
        # Update design.md
        design_file = metis_path / 'design.md'
        updated_design = self._update_planning_document(design_file, project_plan.design_content, 'design')
        with open(design_file, 'w', encoding='utf-8') as f:
            f.write(updated_design)
        files_created['design'] = str(design_file)
        
        # Create session file
        session_file = metis_path / 'session.json'
        self._create_session_file(session_file, project_plan)
        files_created['session'] = str(session_file)
        
        return files_created
    
    def _create_session_file(self, session_file_path, project_plan: ProjectPlan):
        """Create initial session file for project tracking."""
        import json
        from datetime import datetime
        
        session_data = {
            "project_name": getattr(project_plan, 'project_name', 'Untitled Project'),
            "created_at": datetime.now().isoformat(),
            "current_phase": "design",
            "phases": {
                "design": {
                    "status": "active",
                    "started_at": datetime.now().isoformat(),
                    "completed_at": None
                },
                "execution": {
                    "status": "pending",
                    "started_at": None,
                    "completed_at": None
                },
                "review": {
                    "status": "pending",
                    "started_at": None,
                    "completed_at": None
                }
            },
            "iterations": [],
            "git_info": {
                "repository_initialized": True,
                "current_branch": "main",
                "last_commit": None
            },
            "metadata": {
                "original_query": getattr(project_plan, 'original_query', ''),
                "complexity": getattr(project_plan, 'complexity', 'moderate'),
                "project_type": getattr(project_plan, 'project_type', 'general')
            }
        }
        
        with open(session_file_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)
    
    def _update_planning_document(self, file_path, new_content: str, doc_type: str) -> str:
        """Intelligently update existing planning document or create new one."""
        from pathlib import Path
        
        # Ensure file_path is a Path object
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        if not file_path.exists():
            # File doesn't exist, return new content as-is
            print(f"[DEBUG] File {file_path} doesn't exist, creating new")
            return new_content
        
        try:
            # Read existing content
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read().strip()
            
            if not existing_content:
                # Empty file, return new content
                print(f"[DEBUG] File {file_path} is empty, using new content")
                return new_content
            
            print(f"[DEBUG] Merging existing content for {doc_type}")
            # Use LLM to intelligently merge the content
            return self._merge_document_content(existing_content, new_content, doc_type)
            
        except Exception as e:
            # If anything goes wrong, return new content
            print(f"[DEBUG] Error updating {doc_type}: {e}, using new content")
            return new_content
    
    def _merge_document_content(self, existing_content: str, new_content: str, doc_type: str) -> str:
        """Use LLM to intelligently merge existing and new document content."""
        try:
            merge_prompt = f"""You are helping to update a {doc_type} document for a coding project. You need to intelligently merge existing content with new content, preserving valuable information while incorporating updates.

EXISTING CONTENT:
{existing_content}

NEW CONTENT TO INTEGRATE:
{new_content}

Instructions:
1. Preserve all valuable information from the existing content
2. Integrate new information from the new content
3. Remove any duplicate or redundant information
4. Maintain proper markdown formatting
5. Keep the document well-organized and coherent
6. If there are conflicts, prefer the new content but note important changes
7. Add a timestamp comment at the top indicating when it was last updated

Return the merged document:"""
            
            # Get LLM interface
            from .llm_interface import LLMInterface
            llm = LLMInterface()
            response = llm.generate_response(merge_prompt)
            
            # Add update timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            merged_content = f"<!-- Last updated: {timestamp} -->\n\n{response.strip()}"
            
            return merged_content
            
        except Exception as e:
            # Fallback: append new content to existing with separator
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return f"{existing_content}\n\n---\n<!-- Updated: {timestamp} -->\n\n{new_content}"

    def _create_project_structure(self, query: str, coding_analysis) -> dict:
        """Create proper project folder structure."""
        from pathlib import Path
        import re
        
        # Generate project name from query
        project_name = self._generate_project_folder_name(query)
        
        # Create project directory
        current_dir = Path.cwd()
        project_dir = current_dir / project_name
        
        # Handle existing directory
        counter = 1
        original_project_dir = project_dir
        while project_dir.exists():
            project_dir = current_dir / f"{project_name}-{counter}"
            counter += 1
        
        # Create directory structure
        project_dir.mkdir(parents=True, exist_ok=True)
        metis_dir = project_dir / 'Metis'
        metis_dir.mkdir(parents=True, exist_ok=True)
        src_dir = project_dir / 'src'
        src_dir.mkdir(parents=True, exist_ok=True)
        
        return {
            'project_dir': str(project_dir),
            'metis_dir': str(metis_dir),
            'src_dir': str(src_dir),
            'project_name': project_name
        }
    
    def _generate_project_folder_name(self, query: str) -> str:
        """Generate a clean folder name from the project query."""
        import re
        
        # Extract key words and clean them
        words = query.lower().split()
        
        # Remove common words
        stop_words = {'create', 'build', 'make', 'develop', 'a', 'an', 'the', 'for', 'with', 'using'}
        meaningful_words = [word for word in words if word not in stop_words]
        
        # Take first 3-4 meaningful words
        name_words = meaningful_words[:4] if meaningful_words else ['metis', 'project']
        
        # Clean and join
        clean_words = []
        for word in name_words:
            # Remove special characters and keep only alphanumeric
            clean_word = re.sub(r'[^a-zA-Z0-9]', '', word)
            if clean_word:
                clean_words.append(clean_word)
        
        # Join with hyphens
        folder_name = '-'.join(clean_words)
        
        # Ensure it's not empty and not too long
        if not folder_name or len(folder_name) < 3:
            folder_name = 'metis-project'
        elif len(folder_name) > 50:
            folder_name = folder_name[:50]
        
        return folder_name
    
    def _initialize_git_repository(self, project_info: dict):
        """Initialize Git repository with proper structure."""
        try:
            from ..tools.advanced_tools.gitintegration import GitIntegrationTool
            
            project_dir = project_info['project_dir']
            project_name = project_info['project_name']
            
            # Initialize Git repository
            git_tool = GitIntegrationTool()
            
            # Change to project directory and initialize
            import os
            original_cwd = os.getcwd()
            os.chdir(project_dir)
            
            try:
                # Initialize repository
                init_result = git_tool.execute({
                    'action': 'init',
                    'message': f'Initialize {project_name} repository'
                })
                
                # Create initial .gitignore
                self._create_gitignore(project_dir)
                
                # Create initial commit with project structure
                git_tool.execute({
                    'action': 'add',
                    'files': ['.'],
                    'message': 'Add all project files'
                })
                
                git_tool.execute({
                    'action': 'commit',
                    'message': f'Initial commit: {project_name} project structure'
                })
                
                print(f"Git repository initialized in {project_dir}")
                
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            print(f"Warning: Could not initialize Git repository: {e}")
    
    def _create_gitignore(self, project_dir: str):
        """Create a comprehensive .gitignore file."""
        gitignore_content = """# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/
.env

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Temporary files
*.tmp
*.temp
.cache/

# Build outputs
*.o
*.so
*.dylib
*.dll
*.exe

# Configuration files with secrets
.env.local
.env.production
config/secrets.json
"""
        
        gitignore_path = Path(project_dir) / '.gitignore'
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)


class CodingOrchestrator(SmartOrchestrator):
    """Enhanced orchestrator specialized for coding tasks with Git integration."""
    
    def __init__(self, tools_registry: Dict[str, Any] = None):
        super().__init__(tools_registry)
        self.clarification_engine = IntelligentClarificationEngine()
        self.project_planner = IntelligentProjectPlanner()
    
    def analyze_coding_query(self, query: str, context: Dict = None) -> CodingAnalysis:
        """Analyze coding query and determine if clarification is needed."""
        
        # Generate clarification questions
        questions = self.clarification_engine.generate_clarification_questions(query, context)
        
        # Determine complexity and project type
        complexity = self._assess_complexity(query)
        project_type = self._detect_project_type(query)
        
        # Determine missing context
        missing_context = []
        for q in questions:
            missing_context.append(q.category)
        
        return CodingAnalysis(
            query=query,
            complexity=complexity,
            project_type=project_type,
            missing_context=missing_context,
            questions=questions,
            confidence=0.8 if len(questions) <= 2 else 0.6
        )
    
    def execute_with_clarification(self, query: str, context: Dict = None,
                                 interactive_clarification: bool = True) -> ExecutionResult:
        """Execute coding task with optional interactive clarification."""
        
        start_time = time.time()
        
        # Analyze the coding query
        coding_analysis = self.analyze_coding_query(query, context)
        
        # If clarification is needed and we're in interactive mode
        if coding_analysis.requires_clarification and interactive_clarification:
            print(f"\nI need to ask a few questions to create the best solution for: {query}")
            
            responses = []
            for question in coding_analysis.questions:
                print(f"\n[{question.category.upper()}] {question.question}")
                if question.context:
                    print(f"Context: {question.context}")
                
                try:
                    response = input("Your answer: ").strip()
                    responses.append(response)
                except (EOFError, KeyboardInterrupt):
                    print("\nNo interactive input available. Using default responses.")
                    # Use default responses based on question category
                    default_response = self._get_default_response(question)
                    responses.append(default_response)
                    print(f"Using default: {default_response}")
            
            # Process responses into enhanced requirements
            requirements = self.clarification_engine.process_clarification_responses(
                coding_analysis.questions, responses
            )
            
            # Create comprehensive project plan
            project_plan = self.project_planner.create_project_plan(requirements)
            
            # Create project structure and initialize Git
            project_info = self._create_project_structure(query, coding_analysis)
            
            # Generate planning documents in the project's Metis directory
            files_created = self.project_planner.generate_planning_documents(project_plan, project_info['metis_dir'])
            
            # Initialize Git repository
            self._initialize_git_repository(project_info)
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                response=f"Created comprehensive project plan with clarified requirements. Generated files: {', '.join(files_created.keys())}",
                strategy_used="CLARIFICATION_PLANNING",
                tools_used=['ClarificationEngine', 'ProjectPlanner'],
                execution_time=execution_time,
                confidence=coding_analysis.confidence,
                metadata={
                    'clarification_questions': len(coding_analysis.questions),
                    'requirements_enhanced': True,
                    'planning_documents_created': files_created,
                    'project_type': coding_analysis.project_type,
                    'complexity': coding_analysis.complexity.value if hasattr(coding_analysis.complexity, 'value') else str(coding_analysis.complexity)
                },
                error=None
            )
        
        else:
            # Execute without clarification using parent orchestrator
            # Convert CodingAnalysis to QueryAnalysis for compatibility
            query_analysis = QueryAnalysis(
                complexity=coding_analysis.complexity,
                strategy=ExecutionStrategy.SEQUENTIAL,
                confidence=coding_analysis.confidence,
                required_tools=['CodingTool', 'ProjectScaffoldingTool'],
                estimated_steps=3,
                user_intent=f"Coding task: {query}",
                reasoning="Coding task without clarification"
            )
            
            return self.execute(
                analysis=query_analysis,
                tools=context.get('tools', {}) if context else {},
                llm=context.get('llm') if context else None,
                memory_context=context.get('memory_context', '') if context else '',
                session_id=context.get('session_id') if context else None,
                query=query,
                system_message=context.get('system_message') if context else None,
                config=context.get('config') if context else None
            )
    
    def _assess_complexity(self, query: str) -> QueryComplexity:
        """Assess the complexity of a coding query."""
        word_count = len(query.split())
        
        # Complex indicators
        complex_indicators = [
            'system', 'application', 'platform', 'architecture', 'microservice',
            'database', 'api', 'authentication', 'deployment', 'scalable'
        ]
        
        # Simple indicators  
        simple_indicators = [
            'function', 'method', 'script', 'utility', 'helper', 'tool'
        ]
        
        if word_count > 20 or any(indicator in query.lower() for indicator in complex_indicators):
            return QueryComplexity.COMPLEX
        elif word_count > 10 or 'create' in query.lower() or 'build' in query.lower():
            return QueryComplexity.MODERATE
        elif any(indicator in query.lower() for indicator in simple_indicators):
            return QueryComplexity.SIMPLE
        else:
            return QueryComplexity.MODERATE
    
    def _detect_project_type(self, query: str) -> str:
        """Detect the type of project from the query."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['web', 'website', 'webapp', 'frontend', 'backend']):
            return 'web_app'
        elif any(word in query_lower for word in ['api', 'rest', 'endpoint', 'service']):
            return 'api'
        elif any(word in query_lower for word in ['library', 'package', 'module']):
            return 'library'
        elif any(word in query_lower for word in ['cli', 'command', 'tool', 'script']):
            return 'tool'
        elif any(word in query_lower for word in ['mobile', 'app', 'android', 'ios']):
            return 'mobile_app'
        elif any(word in query_lower for word in ['game', 'gaming']):
            return 'game'
        else:
            return 'application'
    
    def _get_default_response(self, question: CodingQuestion) -> str:
        """Get sensible default responses for non-interactive contexts."""
        defaults = {
            'requirements': 'Basic functionality with standard features',
            'tech_stack': 'Python with modern libraries and frameworks',
            'architecture': 'Simple, maintainable architecture following best practices',
            'constraints': 'Standard performance requirements, no special constraints',
            'deployment': 'Local development, can be deployed to common platforms'
        }
        
        # Try to provide more specific defaults based on question content
        question_lower = question.question.lower()
        
        if 'calculator' in question_lower:
            if question.category == 'requirements':
                return 'Basic arithmetic operations (add, subtract, multiply, divide)'
            elif question.category == 'tech_stack':
                return 'Python with command-line interface'
        
        if 'web' in question_lower or 'api' in question_lower:
            if question.category == 'tech_stack':
                return 'Python with Flask/FastAPI framework'
        
        return defaults.get(question.category, 'Standard approach')
    
    def _create_session_file(self, query: str, coding_analysis: CodingAnalysis, output_dir: str):
        """Create session.json file for session management."""
        from pathlib import Path
        import json
        
        # Create session data
        session_data = {
            'session_id': f"metis-coding-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'project_name': self._extract_project_name(query),
            'project_description': query,
            'current_phase': 'design',
            'iteration': 1,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'phases_completed': [],
            'phase_history': [{
                'event': 'session_start',
                'phase': 'design',
                'timestamp': datetime.now().isoformat(),
                'iteration': 1
            }],
            'progress': {
                'tasks_completed': 0,
                'tasks_total': 0,
                'completion_percentage': 0
            },
            'metadata': {
                'project_type': coding_analysis.project_type,
                'complexity': coding_analysis.complexity.value if hasattr(coding_analysis.complexity, 'value') else str(coding_analysis.complexity),
                'confidence': coding_analysis.confidence
            }
        }
        
        # Save to Metis directory
        base_path = Path(output_dir).resolve()
        metis_path = base_path / 'Metis'
        metis_path.mkdir(parents=True, exist_ok=True)
        
        session_file = metis_path / 'session.json'
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)
    
    def _extract_project_name(self, description: str) -> str:
        """Extract a project name from the description."""
        # Simple extraction - take first few words and clean them
        words = description.lower().split()[:4]
        name_words = []
        
        for word in words:
            # Skip common words
            if word not in ['create', 'build', 'make', 'develop', 'a', 'an', 'the']:
                name_words.append(word.capitalize())
        
        if not name_words:
            name_words = ['Metis', 'Project']
        
        return ' '.join(name_words)
    
    def _create_project_structure(self, query: str, coding_analysis) -> dict:
        """Create proper project folder structure."""
        from pathlib import Path
        import re
        
        # Generate project name from query
        project_name = self._generate_project_folder_name(query)
        
        # Create project directory
        current_dir = Path.cwd()
        project_dir = current_dir / project_name
        
        # Handle existing directory
        counter = 1
        original_project_dir = project_dir
        while project_dir.exists():
            project_dir = current_dir / f"{project_name}-{counter}"
            counter += 1
        
        # Create directory structure
        project_dir.mkdir(parents=True, exist_ok=True)
        metis_dir = project_dir / 'Metis'
        metis_dir.mkdir(parents=True, exist_ok=True)
        src_dir = project_dir / 'src'
        src_dir.mkdir(parents=True, exist_ok=True)
        
        return {
            'project_dir': str(project_dir),
            'metis_dir': str(metis_dir),
            'src_dir': str(src_dir),
            'project_name': project_name
        }
    
    def _generate_project_folder_name(self, query: str) -> str:
        """Generate a clean folder name from the project query."""
        import re
        
        # Extract key words and clean them
        words = query.lower().split()
        
        # Remove common words
        stop_words = {'create', 'build', 'make', 'develop', 'a', 'an', 'the', 'for', 'with', 'using'}
        meaningful_words = [word for word in words if word not in stop_words]
        
        # Take first 3-4 meaningful words
        name_words = meaningful_words[:4] if meaningful_words else ['metis', 'project']
        
        # Clean and join
        clean_words = []
        for word in name_words:
            # Remove special characters and keep only alphanumeric
            clean_word = re.sub(r'[^a-zA-Z0-9]', '', word)
            if clean_word:
                clean_words.append(clean_word)
        
        # Join with hyphens
        folder_name = '-'.join(clean_words)
        
        # Ensure it's not empty and not too long
        if not folder_name or len(folder_name) < 3:
            folder_name = 'metis-project'
        elif len(folder_name) > 50:
            folder_name = folder_name[:50]
        
        return folder_name
    
    def _initialize_git_repository(self, project_info: dict):
        """Initialize Git repository with proper structure."""
        try:
            from ..tools.advanced_tools.gitintegration import GitIntegrationTool
            
            project_dir = project_info['project_dir']
            project_name = project_info['project_name']
            
            # Initialize Git repository
            git_tool = GitIntegrationTool()
            
            # Change to project directory and initialize
            import os
            original_cwd = os.getcwd()
            os.chdir(project_dir)
            
            try:
                # Initialize repository
                init_result = git_tool.execute({
                    'action': 'init',
                    'message': f'Initialize {project_name} repository'
                })
                
                # Create initial .gitignore
                self._create_gitignore(project_dir)
                
                # Create initial commit with project structure
                git_tool.execute({
                    'action': 'add',
                    'files': ['.'],
                    'message': 'Add all project files'
                })
                
                git_tool.execute({
                    'action': 'commit',
                    'message': f'Initial commit: {project_name} project structure'
                })
                
                print(f"Git repository initialized in {project_dir}")
                
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            print(f"Warning: Could not initialize Git repository: {e}")
    
    def _create_gitignore(self, project_dir: str):
        """Create a comprehensive .gitignore file."""
        gitignore_content = """# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/
.env

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Temporary files
*.tmp
*.temp
.cache/

# Build outputs
*.o
*.so
*.dylib
*.dll
*.exe

# Configuration files with secrets
.env.local
.env.production
config/secrets.json
"""
        
        gitignore_path = Path(project_dir) / '.gitignore'
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)


class CodingOrchestrator(SmartOrchestrator):
    """Enhanced orchestrator specialized for coding tasks with Git integration."""
    
    def __init__(self, tools_registry: Dict[str, Any] = None):
        super().__init__(tools_registry)
        self.clarification_engine = IntelligentClarificationEngine()
        self.project_planner = IntelligentProjectPlanner()
    
    def analyze_coding_query(self, query: str, context: Dict = None) -> CodingAnalysis:
        """Analyze coding query and determine if clarification is needed."""
        
        # Generate clarification questions
        questions = self.clarification_engine.generate_clarification_questions(query, context)
        
        # Determine complexity and project type
        complexity = self._assess_complexity(query)
        project_type = self._detect_project_type(query)
        
        # Determine missing context
        missing_context = []
        for q in questions:
            missing_context.append(q.category)
        
        return CodingAnalysis(
            query=query,
            complexity=complexity,
            project_type=project_type,
            missing_context=missing_context,
            questions=questions,
            confidence=0.8 if len(questions) <= 2 else 0.6
        )
    
    def execute_with_clarification(self, query: str, context: Dict = None,
                                 interactive_clarification: bool = True) -> ExecutionResult:
        """Execute coding task with optional interactive clarification and Git integration."""
        
        start_time = time.time()
        
        # Analyze the coding query
        coding_analysis = self.analyze_coding_query(query, context)
        
        # If clarification is needed and we're in interactive mode
        if coding_analysis.requires_clarification and interactive_clarification:
            print(f"\nI need to ask a few questions to create the best solution for: {query}")
            
            responses = []
            for question in coding_analysis.questions:
                print(f"\n[{question.category.upper()}] {question.question}")
                if question.context:
                    print(f"Context: {question.context}")
                
                try:
                    response = input("Your answer: ").strip()
                    responses.append(response)
                except (EOFError, KeyboardInterrupt):
                    print("\nNo interactive input available. Using default responses.")
                    # Use default responses based on question category
                    default_response = self._get_default_response(question)
                    responses.append(default_response)
                    print(f"Using default: {default_response}")
            
            # Process responses into enhanced requirements
            requirements = self.clarification_engine.process_clarification_responses(
                coding_analysis.questions, responses
            )
            
            # Create comprehensive project plan
            project_plan = self.project_planner.create_project_plan(requirements)
            
            # Create project structure and initialize Git
            project_info = self.project_planner._create_project_structure(query, coding_analysis)
            
            # Generate planning documents in the project's Metis directory
            files_created = self.project_planner.generate_planning_documents(project_plan, project_info['metis_dir'])
            
            # Create session file
            self.project_planner._create_session_file(query, coding_analysis, project_info['metis_dir'])
            
            # Initialize Git repository
            self.project_planner._initialize_git_repository(project_info)
            
            execution_time = time.time() - start_time
            
            # Display project creation summary
            print(f"\nProject created successfully!")
            print(f"Project directory: {project_info['project_dir']}")
            print(f"Planning documents in: {project_info['metis_dir']}")
            print(f"Source code directory: {project_info['src_dir']}")
            print(f"Git repository initialized with initial commit")
            
            return ExecutionResult(
                response=f"Created comprehensive project plan with clarified requirements. Generated files: {', '.join(files_created.keys())}",
                strategy_used="CLARIFICATION_PLANNING_GIT",
                tools_used=['ClarificationEngine', 'ProjectPlanner', 'GitIntegrationTool'],
                execution_time=execution_time,
                confidence=coding_analysis.confidence,
                metadata={
                    'clarification_questions': len(coding_analysis.questions),
                    'requirements_enhanced': True,
                    'planning_documents_created': files_created,
                    'project_type': coding_analysis.project_type,
                    'complexity': coding_analysis.complexity.value if hasattr(coding_analysis.complexity, 'value') else str(coding_analysis.complexity),
                    'project_info': project_info,
                    'git_initialized': True
                },
                error=None
            )
        
        else:
            # Execute without clarification using parent orchestrator
            # Convert CodingAnalysis to QueryAnalysis for compatibility
            query_analysis = QueryAnalysis(
                complexity=coding_analysis.complexity,
                strategy=ExecutionStrategy.SEQUENTIAL,
                confidence=coding_analysis.confidence,
                required_tools=['CodingTool', 'ProjectScaffoldingTool'],
                estimated_steps=3,
                user_intent=f"Coding task: {query}",
                reasoning="Coding task without clarification"
            )
            
            return self.execute(
                analysis=query_analysis,
                tools=context.get('tools', {}) if context else {},
                llm=context.get('llm') if context else None,
                memory_context=context.get('memory_context', '') if context else '',
                session_id=context.get('session_id') if context else None,
                query=query,
                system_message=context.get('system_message') if context else None,
                config=context.get('config') if context else None
            )
    
    def _assess_complexity(self, query: str) -> QueryComplexity:
        """Assess the complexity of a coding query."""
        word_count = len(query.split())
        
        # Complex indicators
        complex_indicators = [
            'system', 'application', 'platform', 'architecture', 'microservice',
            'database', 'api', 'authentication', 'deployment', 'scalable'
        ]
        
        # Simple indicators  
        simple_indicators = [
            'function', 'method', 'script', 'utility', 'helper', 'tool'
        ]
        
        if word_count > 20 or any(indicator in query.lower() for indicator in complex_indicators):
            return QueryComplexity.COMPLEX
        elif word_count > 10 or 'create' in query.lower() or 'build' in query.lower():
            return QueryComplexity.MODERATE
        elif any(indicator in query.lower() for indicator in simple_indicators):
            return QueryComplexity.SIMPLE
        else:
            return QueryComplexity.MODERATE
    
    def _detect_project_type(self, query: str) -> str:
        """Detect the type of project from the query."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['web', 'website', 'webapp', 'frontend', 'backend']):
            return 'web_app'
        elif any(word in query_lower for word in ['api', 'rest', 'endpoint', 'service']):
            return 'api'
        elif any(word in query_lower for word in ['library', 'package', 'module']):
            return 'library'
        elif any(word in query_lower for word in ['cli', 'command', 'tool', 'script']):
            return 'tool'
        elif any(word in query_lower for word in ['mobile', 'app', 'android', 'ios']):
            return 'mobile_app'
        elif any(word in query_lower for word in ['game', 'gaming']):
            return 'game'
        else:
            return 'application'
    
    def _get_default_response(self, question: CodingQuestion) -> str:
        """Get sensible default responses for non-interactive contexts."""
        defaults = {
            'requirements': 'Basic functionality with standard features',
            'tech_stack': 'Python with modern libraries and frameworks',
            'architecture': 'Simple, maintainable architecture following best practices',
            'constraints': 'Standard performance requirements, no special constraints',
            'deployment': 'Local development, can be deployed to common platforms'
        }
        
        # Try to provide more specific defaults based on question content
        question_lower = question.question.lower()
        
        if 'calculator' in question_lower:
            if question.category == 'requirements':
                return 'Basic arithmetic operations (add, subtract, multiply, divide)'
            elif question.category == 'tech_stack':
                return 'Python with command-line interface'
        
        if 'web' in question_lower or 'api' in question_lower:
            if question.category == 'tech_stack':
                return 'Python with Flask/FastAPI framework'
        
        return defaults.get(question.category, 'Standard approach')
