"""
.metis File Parser

Handles parsing of .metis files for project-specific configurations,
similar to .claude files but tailored for Metis multi-agent system.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


class MetisFileParser:
    """Parser for .metis configuration files."""
    
    def __init__(self):
        self.supported_sections = {
            'instructions', 'agent', 'commands', 'tools', 
            'memory', 'knowledge', 'workflows', 'shortcuts'
        }
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a .metis file and return configuration dictionary.
        
        .metis file format:
        ```
        # Project Instructions
        Custom instructions for this project...
        
        ## Agent Configuration
        agent:
          default_profile: developer
          preferred_model: claude-3-sonnet
          multi_agent_mode: true
          
        ## Custom Commands  
        commands:
          /deploy: "Deploy to staging with tests"
          /review: "@senior-dev review this code"
        
        ## Tools Configuration
        tools:
          enabled: [filesystem, git, e2b]
          disabled: [web_scraper]
          
        ## Memory Settings
        memory:
          persist_context: true
          titans_mode: true
          
        ## Knowledge Base
        knowledge:
          auto_index: true
          categories: [code, docs, architecture]
        ```
        """
        if not file_path.exists():
            return {}
        
        try:
            content = file_path.read_text(encoding='utf-8')
            return self._parse_content(content)
        except Exception as e:
            raise ValueError(f"Error parsing .metis file: {e}")
    
    def _parse_content(self, content: str) -> Dict[str, Any]:
        """Parse the content of a .metis file."""
        config = {}
        
        # Split content by sections
        sections = self._split_into_sections(content)
        
        for section_name, section_content in sections.items():
            if section_name == 'instructions':
                config['instructions'] = section_content.strip()
            else:
                # Try to parse as YAML
                try:
                    parsed = yaml.safe_load(section_content)
                    if parsed:
                        config[section_name] = parsed
                except yaml.YAMLError:
                    # If YAML parsing fails, store as text
                    config[section_name] = section_content.strip()
        
        return config
    
    def _split_into_sections(self, content: str) -> Dict[str, str]:
        """Split content into sections based on headers."""
        sections = {}
        current_section = 'instructions'  # Default section
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            # Check for section headers (## Section Name)
            header_match = re.match(r'^##\s+(.+)', line.strip())
            if header_match:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                section_name = header_match.group(1).lower().replace(' ', '_')
                section_name = re.sub(r'[^a-z0-9_]', '', section_name)
                current_section = section_name
                current_content = []
            else:
                current_content.append(line)
        
        # Save final section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def create_template(self, file_path: Path, project_type: str = "general"):
        """Create a template .metis file for a project."""
        templates = {
            "general": self._get_general_template(),
            "web": self._get_web_template(),
            "api": self._get_api_template(),
            "data": self._get_data_template(),
            "ml": self._get_ml_template()
        }
        
        template = templates.get(project_type, templates["general"])
        
        file_path.write_text(template, encoding='utf-8')
    
    def create_enhanced_template(self, file_path: Path, project_type: str = "general"):
        """Create an enhanced .metis file template focused on custom instructions and IDE integration."""
        templates = {
            "general": self._get_enhanced_general_template(),
            "web": self._get_enhanced_web_template(),
            "api": self._get_enhanced_api_template(),
            "data": self._get_enhanced_data_template(),
            "ml": self._get_enhanced_ml_template(),
            "react": self._get_enhanced_react_template(),
            "python": self._get_enhanced_python_template(),
            "typescript": self._get_enhanced_typescript_template()
        }
        
        template = templates.get(project_type, templates["general"])
        
        file_path.write_text(template, encoding='utf-8')
    
    def _get_general_template(self) -> str:
        return """# Project Instructions
You are working on a software project. Please follow these guidelines:
- Write clean, well-documented code
- Follow existing code style and patterns
- Ask for clarification when requirements are unclear

## Agent Configuration
agent:
  default_profile: developer
  preferred_model: claude-3-sonnet
  multi_agent_mode: false

## Custom Commands
commands:
  /review: "Review the current changes"
  /test: "Run the test suite"
  /docs: "Generate documentation"

## Tools Configuration  
tools:
  enabled: [filesystem, git, python_code]
  auto_enable: true

## Memory Settings
memory:
  persist_context: true
  titans_mode: false

## Knowledge Base
knowledge:
  auto_index: true
  categories: [code, docs]
"""

    def _get_web_template(self) -> str:
        return """# Web Development Project
You are working on a web application. Focus on:
- Modern web standards and best practices
- Responsive design principles
- Security considerations
- Performance optimization

## Agent Configuration
agent:
  default_profile: developer
  preferred_model: claude-3-sonnet
  multi_agent_mode: true
  
## Custom Commands
commands:
  /deploy: "@devops deploy to staging"
  /review: "@senior-dev review frontend code"
  /test: "Run frontend and backend tests"
  /lint: "Run code quality checks"

## Tools Configuration
tools:
  enabled: [filesystem, git, web_scraper, e2b]
  
## Workflows
workflows:
  pre_commit:
    - /lint
    - /test
    - "@qa validate changes"
"""

    def _get_api_template(self) -> str:
        return """# API Development Project  
You are working on an API service. Focus on:
- RESTful design principles
- Proper error handling and status codes
- API documentation and testing
- Security and authentication

## Agent Configuration
agent:
  default_profile: developer
  preferred_model: claude-3-sonnet
  multi_agent_mode: true

## Custom Commands
commands:
  /test-api: "Run API integration tests"
  /docs: "Generate API documentation"
  /deploy: "@devops deploy API to staging"
  /security: "@security-expert review API endpoints"

## Tools Configuration
tools:
  enabled: [filesystem, git, python_code, web_scraper]
"""

    def _get_data_template(self) -> str:
        return """# Data Science Project
You are working on a data analysis/science project. Focus on:
- Data quality and validation
- Reproducible analysis workflows
- Clear visualization and reporting
- Statistical rigor and methodology

## Agent Configuration  
agent:
  default_profile: data_science
  preferred_model: claude-3-sonnet
  multi_agent_mode: true

## Custom Commands
commands:
  /analyze: "Perform data analysis"
  /visualize: "Create data visualizations" 
  /validate: "@data-expert validate methodology"
  /report: "Generate analysis report"

## Tools Configuration
tools:
  enabled: [filesystem, python_code, data_analysis, advanced_math]
"""

    def _get_ml_template(self) -> str:
        return """# Machine Learning Project
You are working on a machine learning project. Focus on:
- Model development and evaluation
- Data preprocessing and feature engineering
- Model deployment and monitoring
- MLOps best practices

## Agent Configuration
agent:
  default_profile: data_science
  preferred_model: claude-3-sonnet
  multi_agent_mode: true

## Custom Commands  
commands:
  /train: "Train ML model"
  /evaluate: "Evaluate model performance"
  /deploy: "@mlops deploy model to production"
  /monitor: "Check model performance metrics"

## Tools Configuration
tools:
  enabled: [filesystem, python_code, data_analysis, advanced_math, e2b]
  
## Memory Settings
memory:
  persist_context: true
  titans_mode: true
"""

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate .metis configuration and return any warnings."""
        warnings = []
        
        # Check for unknown sections
        for section in config.keys():
            if section not in self.supported_sections:
                warnings.append(f"Unknown section: {section}")
        
        # Validate agent configuration
        if 'agent' in config:
            agent_config = config['agent']
            if not isinstance(agent_config, dict):
                warnings.append("Agent configuration must be a dictionary")
            else:
                # Check for valid agent profiles
                valid_profiles = ['developer', 'senior_developer', 'data_science', 'research', 'content_creator']
                if 'default_profile' in agent_config:
                    if agent_config['default_profile'] not in valid_profiles:
                        warnings.append(f"Unknown agent profile: {agent_config['default_profile']}")
        
        # Validate commands
        if 'commands' in config:
            commands = config['commands']
            if not isinstance(commands, dict):
                warnings.append("Commands section must be a dictionary")
        
        return warnings
    
    # Enhanced template methods with better custom instruction focus
    def _get_enhanced_general_template(self) -> str:
        return """# Custom Instructions for Metis Agent

## 📝 CUSTOM INSTRUCTIONS
Write your specific instructions here. These will be applied to all AI interactions in this project.

Example instructions:
- Use TypeScript instead of JavaScript
- Follow specific coding standards or style guides  
- Prefer certain libraries or frameworks
- Apply domain-specific knowledge or constraints
- Use particular naming conventions

## 🤖 Agent Configuration
agent:
  default_profile: developer
  preferred_model: claude-3-sonnet
  multi_agent_mode: false
  custom_instructions_priority: high

## 💬 Custom Slash Commands  
commands:
  /setup: "Set up development environment for this project"
  /test: "Run the appropriate test suite"
  /deploy: "Deploy to staging environment"
  /docs: "Generate or update documentation"
  /review: "Review recent changes for quality and standards"

## 🛠️ Tools Configuration
tools:
  enabled: [filesystem, git, python_code]
  auto_enable: true
  security_level: standard

## 📚 Knowledge & Context
knowledge:
  auto_index: true
  categories: [code, docs, architecture]
  custom_context: |
    Add any project-specific context, terminology, or domain knowledge here.
    This helps the AI understand your project better.

## 🔄 Workflows
workflows:
  development:
    - "Follow coding standards"
    - "Write tests for new features" 
    - "Update documentation"
  
  review:
    - "Check code quality"
    - "Verify tests pass"
    - "Ensure documentation is current"

---
💡 USAGE TIPS:
• Edit this file in your IDE for better syntax highlighting
• Use 'metis chat' to start AI session with these settings
• Use '/project config' to view current configuration
• Restart Metis after major changes to reload settings
"""

    def _get_enhanced_react_template(self) -> str:
        return """# Custom Instructions for React Project

## 📝 CUSTOM INSTRUCTIONS
You are working on a React application. Follow these specific guidelines:

- Use TypeScript for all new components and logic
- Prefer functional components with hooks over class components
- Use React Query for data fetching and state management
- Follow component composition patterns and prop drilling avoidance
- Implement proper error boundaries and loading states
- Use React.memo for performance optimization when appropriate
- Follow accessibility best practices (ARIA labels, semantic HTML)
- Use CSS Modules or styled-components for styling

## 🤖 Agent Configuration
agent:
  default_profile: developer
  preferred_model: claude-3-sonnet
  multi_agent_mode: true
  react_expertise: true

## 💬 Custom Slash Commands
commands:
  /component: "Create a new React component with TypeScript"
  /hook: "Create a custom React hook"
  /test: "Run Jest and React Testing Library tests"
  /storybook: "Generate Storybook stories for components"
  /lint: "Run ESLint and Prettier"
  /build: "Build the React application"

## 🛠️ Tools Configuration
tools:
  enabled: [filesystem, git, web_scraper, e2b]
  react_tools: true
  typescript_support: true

## 📚 Knowledge & Context
knowledge:
  categories: [react, typescript, testing, accessibility]
  frameworks: [React, Next.js, React Query, TypeScript]
  testing: [Jest, React Testing Library, Cypress]
  custom_context: |
    This is a React application focusing on [describe your app's purpose].
    Key features include: [list main features]
    Target users: [describe user base]
    Performance requirements: [describe performance needs]

## 🔄 Workflows
workflows:
  component_development:
    - "Create component with TypeScript interface"
    - "Add unit tests with React Testing Library"
    - "Create Storybook story"
    - "Implement accessibility features"
  
  feature_complete:
    - "Run all tests"
    - "Check bundle size impact"
    - "Update documentation"
    - "Verify accessibility compliance"
"""

    def _get_enhanced_python_template(self) -> str:
        return """# Custom Instructions for Python Project

## 📝 CUSTOM INSTRUCTIONS
You are working on a Python project. Follow these specific guidelines:

- Use Python 3.9+ features and type hints for all functions
- Follow PEP 8 style guide and use Black for formatting
- Prefer dataclasses or Pydantic models for data structures
- Use context managers for resource management
- Implement proper error handling with custom exceptions
- Write docstrings following Google or NumPy style
- Use pytest for testing with good coverage
- Follow SOLID principles and clean architecture patterns

## 🤖 Agent Configuration
agent:
  default_profile: developer
  preferred_model: claude-3-sonnet
  python_expertise: true
  code_quality_focus: high

## 💬 Custom Slash Commands
commands:
  /test: "Run pytest with coverage report"
  /lint: "Run flake8, mypy, and black"
  /format: "Format code with black and isort"
  /deps: "Update requirements.txt or pyproject.toml"
  /docs: "Generate documentation with Sphinx"
  /package: "Build and check package with setuptools"

## 🛠️ Tools Configuration
tools:
  enabled: [filesystem, git, python_code, advanced_math]
  python_version: "3.9+"
  type_checking: true

## 📚 Knowledge & Context
knowledge:
  categories: [python, testing, packaging, documentation]
  frameworks: [FastAPI, Django, Flask, SQLAlchemy]
  testing: [pytest, coverage, tox]
  custom_context: |
    This Python project is [describe project type: web API, CLI tool, library, etc.]
    Key dependencies: [list main dependencies]
    Target Python version: [specify version]
    Deployment target: [Docker, cloud, package index, etc.]

## 🔄 Workflows
workflows:
  development:
    - "Write type-annotated code"
    - "Add comprehensive tests"
    - "Update docstrings"
    - "Run linting and formatting"
  
  release:
    - "Run full test suite"
    - "Update version numbers"
    - "Generate changelog"
    - "Build and test package"
"""

    def _get_enhanced_typescript_template(self) -> str:
        return """# Custom Instructions for TypeScript Project

## 📝 CUSTOM INSTRUCTIONS
You are working on a TypeScript project. Follow these specific guidelines:

- Use strict TypeScript configuration with strict mode enabled
- Prefer interfaces over types for object shapes
- Use enums for constants and union types for variants
- Implement proper generic constraints and utility types
- Use ES6+ features and async/await over promises
- Follow functional programming patterns where appropriate
- Implement proper error handling with Result/Either patterns
- Use ESLint with TypeScript rules and Prettier for formatting

## 🤖 Agent Configuration
agent:
  default_profile: developer
  preferred_model: claude-3-sonnet
  typescript_expertise: true
  modern_javascript: true

## 💬 Custom Slash Commands
commands:
  /build: "Compile TypeScript and run build process"
  /test: "Run Jest or Vitest with TypeScript"
  /lint: "Run ESLint with TypeScript rules"
  /types: "Generate or update type definitions"
  /check: "Run TypeScript compiler check"
  /docs: "Generate TypeDoc documentation"

## 🛠️ Tools Configuration
tools:
  enabled: [filesystem, git, web_scraper, e2b]
  typescript_support: true
  node_version: "18+"

## 📚 Knowledge & Context
knowledge:
  categories: [typescript, javascript, testing, tooling]
  frameworks: [Node.js, Express, Fastify, Next.js]
  testing: [Jest, Vitest, Playwright]
  custom_context: |
    This TypeScript project is [describe: backend API, frontend app, library, CLI tool]
    Build target: [Node.js version, browser support, etc.]
    Key frameworks: [list main frameworks and libraries]
    Architecture pattern: [MVC, hexagonal, microservices, etc.]

## 🔄 Workflows
workflows:
  development:
    - "Write type-safe code with proper interfaces"
    - "Add unit tests with good mocking"
    - "Run TypeScript compiler checks"
    - "Ensure proper error handling"
  
  deployment:
    - "Run full build process"
    - "Execute test suite"
    - "Check bundle size"
    - "Validate type definitions"
"""

    def _get_enhanced_web_template(self) -> str:
        return """# Custom Instructions for Web Development Project

## 📝 CUSTOM INSTRUCTIONS
You are working on a web application. Follow these specific guidelines:

- Use semantic HTML5 elements and ensure accessibility compliance
- Implement responsive design with mobile-first approach
- Use modern CSS features (Grid, Flexbox, Custom Properties)
- Follow web performance best practices (lazy loading, optimization)
- Ensure cross-browser compatibility and progressive enhancement
- Implement proper SEO practices and meta tags
- Use modern JavaScript (ES6+) and consider framework patterns
- Prioritize security practices (CSP, HTTPS, input validation)

## 🤖 Agent Configuration
agent:
  default_profile: developer
  preferred_model: claude-3-sonnet
  web_expertise: true
  accessibility_focus: high

## 💬 Custom Slash Commands
commands:
  /lighthouse: "Run Lighthouse performance audit"
  /a11y: "Check accessibility compliance"
  /test: "Run end-to-end and unit tests"
  /build: "Build and optimize for production"
  /serve: "Start development server"
  /deploy: "Deploy to hosting platform"

## 🛠️ Tools Configuration
tools:
  enabled: [filesystem, git, web_scraper, e2b]
  web_dev_tools: true
  accessibility_tools: true

## 📚 Knowledge & Context
knowledge:
  categories: [html, css, javascript, accessibility, performance]
  frameworks: [specify your frontend framework]
  tools: [Webpack, Vite, PostCSS, etc.]
  custom_context: |
    This web application is [describe purpose and target audience]
    Browser support: [specify browser requirements]
    Performance goals: [specify targets like Core Web Vitals]
    Accessibility level: [WCAG 2.1 AA, AAA, etc.]

## 🔄 Workflows
workflows:
  feature_development:
    - "Design with accessibility in mind"
    - "Implement responsive design"
    - "Test across target browsers"
    - "Optimize for performance"
  
  deployment:
    - "Run performance audits"
    - "Check accessibility compliance"
    - "Validate HTML and CSS"
    - "Test on real devices"
"""

    def _get_enhanced_api_template(self) -> str:
        return """# Custom Instructions for API Development Project

## 📝 CUSTOM INSTRUCTIONS
You are working on an API service. Follow these specific guidelines:

- Design RESTful APIs with proper HTTP methods and status codes
- Implement comprehensive input validation and sanitization
- Use OpenAPI/Swagger for API documentation and contract-first development
- Implement proper authentication and authorization mechanisms
- Follow API versioning best practices
- Ensure comprehensive error handling with structured error responses
- Implement rate limiting and security headers
- Use database transactions and connection pooling appropriately

## 🤖 Agent Configuration
agent:
  default_profile: developer
  preferred_model: claude-3-sonnet
  api_expertise: true
  security_focus: high

## 💬 Custom Slash Commands
commands:
  /docs: "Generate OpenAPI documentation"
  /test-api: "Run API integration tests"
  /security: "Run security audit and checks"
  /load-test": "Perform load testing"
  /migrate": "Run database migrations"
  /deploy": "Deploy API to staging/production"

## 🛠️ Tools Configuration
tools:
  enabled: [filesystem, git, python_code, web_scraper]
  api_testing: true
  security_scanning: true

## 📚 Knowledge & Context
knowledge:
  categories: [api, security, database, testing, documentation]
  frameworks: [FastAPI, Express, Django REST, Spring Boot]
  databases: [PostgreSQL, MongoDB, Redis]
  custom_context: |
    This API serves [describe API purpose and main use cases]
    Authentication method: [JWT, OAuth2, API keys, etc.]
    Database: [specify database and ORM/query builder]
    Expected load: [requests per second, concurrent users]

## 🔄 Workflows
workflows:
  api_development:
    - "Design API contract with OpenAPI"
    - "Implement with proper validation"
    - "Add comprehensive tests"
    - "Update documentation"
  
  deployment:
    - "Run security scans"
    - "Execute load tests"
    - "Validate API documentation"
    - "Check monitoring and logging"
"""

    def _get_enhanced_data_template(self) -> str:
        return """# Custom Instructions for Data Science Project

## 📝 CUSTOM INSTRUCTIONS
You are working on a data science project. Follow these specific guidelines:

- Use reproducible research practices with version control for data and code
- Implement proper data validation and quality checks
- Follow data preprocessing pipelines with clear documentation
- Use appropriate statistical methods and validate assumptions
- Create clear visualizations that tell the data story effectively
- Implement proper model evaluation and cross-validation techniques
- Document methodology, assumptions, and limitations clearly
- Ensure ethical considerations around data privacy and bias

## 🤖 Agent Configuration
agent:
  default_profile: data_science
  preferred_model: claude-3-sonnet
  statistical_expertise: true
  visualization_focus: high

## 💬 Custom Slash Commands
commands:
  /eda: "Perform exploratory data analysis"
  /clean: "Run data cleaning and preprocessing"
  /model: "Train and evaluate machine learning models"
  /viz: "Create data visualizations and reports"
  /test: "Run statistical tests and validations"
  /report: "Generate analysis report"

## 🛠️ Tools Configuration
tools:
  enabled: [filesystem, python_code, data_analysis, advanced_math]
  statistical_packages: true
  visualization_tools: true

## 📚 Knowledge & Context
knowledge:
  categories: [statistics, machine_learning, visualization, data_ethics]
  libraries: [pandas, numpy, scikit-learn, matplotlib, seaborn]
  methods: [specify preferred statistical or ML methods]
  custom_context: |
    This data science project focuses on [describe problem domain]
    Data sources: [describe data types and sources]
    Target outcomes: [prediction, classification, insights, etc.]
    Constraints: [computational, ethical, business constraints]

## 🔄 Workflows
workflows:
  analysis:
    - "Explore and understand the data"
    - "Clean and preprocess data"
    - "Apply appropriate statistical methods"
    - "Validate results and assumptions"
  
  modeling:
    - "Feature engineering and selection"
    - "Model training with cross-validation"
    - "Evaluate model performance"
    - "Document model limitations and bias"
"""

    def _get_enhanced_ml_template(self) -> str:
        return """# Custom Instructions for Machine Learning Project

## 📝 CUSTOM INSTRUCTIONS
You are working on a machine learning project. Follow these specific guidelines:

- Implement MLOps best practices with experiment tracking and model versioning
- Use proper train/validation/test splits and cross-validation strategies
- Implement feature engineering pipelines that are reproducible and scalable
- Apply appropriate model selection techniques and hyperparameter tuning
- Ensure model interpretability and fairness evaluation
- Implement model monitoring and drift detection in production
- Document model architecture, training process, and performance metrics
- Consider computational efficiency and deployment constraints

## 🤖 Agent Configuration
agent:
  default_profile: data_science
  preferred_model: claude-3-sonnet
  ml_expertise: true
  mlops_focus: high

## 💬 Custom Slash Commands
commands:
  /train: "Train machine learning models"
  /tune: "Perform hyperparameter tuning"
  /evaluate: "Evaluate model performance"
  /deploy: "Deploy model to production"
  /monitor: "Check model performance metrics"
  /experiment": "Run ML experiments with tracking"

## 🛠️ Tools Configuration
tools:
  enabled: [filesystem, python_code, data_analysis, advanced_math, e2b]
  ml_frameworks: true
  experiment_tracking: true

## 📚 Knowledge & Context
knowledge:
  categories: [machine_learning, deep_learning, mlops, model_deployment]
  frameworks: [scikit-learn, TensorFlow, PyTorch, MLflow]
  deployment: [Docker, Kubernetes, cloud platforms]
  custom_context: |
    This ML project aims to [describe ML objective: classification, regression, etc.]
    Model type: [traditional ML, deep learning, ensemble, etc.]
    Data scale: [size, dimensions, real-time requirements]
    Deployment target: [cloud, edge, batch processing, real-time API]

## 🔄 Workflows
workflows:
  experimentation:
    - "Design and track experiments"
    - "Implement feature engineering"
    - "Train and validate models"
    - "Compare model performance"
  
  production:
    - "Prepare model for deployment"
    - "Set up monitoring and logging"
    - "Implement A/B testing"
    - "Monitor model drift and performance"
"""