"""
Knowledge Base Configuration

Handles configuration for the knowledge base system including categories,
templates, modules, and external providers.
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class CategoryConfig:
    """Configuration for a knowledge category"""
    name: str
    description: str = ""
    icon: str = "📄"
    subcategories: List[str] = field(default_factory=list)
    templates: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "icon": self.icon,
            "subcategories": self.subcategories,
            "templates": self.templates
        }


@dataclass
class ModuleConfig:
    """Configuration for a knowledge module"""
    name: str
    enabled: bool = True
    class_name: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "class": self.class_name,
            "config": self.config
        }


class KnowledgeConfig:
    """
    Knowledge base configuration management
    """
    
    def __init__(self, knowledge_dir: str = "knowledge"):
        self.knowledge_dir = knowledge_dir
        self.config_dir = os.path.join(knowledge_dir, "config")
        
        # Core settings
        self.enabled = True
        self.local_storage_path = knowledge_dir
        self.database_path = os.path.join(knowledge_dir, "knowledge.db")
        self.external_provider = None  # local, supabase, postgresql, mongodb
        self.external_config = {}
        self.auto_learning = True
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        self.max_context_entries = 10
        self.similarity_threshold = 0.7
        self.auto_sync_interval = 3600  # 1 hour
        
        # Graph-specific settings
        self.enable_graph = True
        self.graph_cache_size = 1000
        self.max_relationship_depth = 3
        self.auto_detect_relationships = True
        self.relationship_strength_threshold = 0.3
        self.graph_rebuild_interval = 3600  # seconds
        self.enable_semantic_embeddings = False
        
        # Categories and modules
        self.categories: Dict[str, CategoryConfig] = {}
        self.modules: Dict[str, ModuleConfig] = {}
        self.default_templates: Dict[str, str] = {}
        
        # Initialize directories and load config
        self._ensure_directories()
        self._load_config()
    
    def _ensure_directories(self):
        """Ensure all necessary directories exist"""
        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(os.path.join(self.knowledge_dir, "ai_insights"), exist_ok=True)
    
    def _load_config(self):
        """Load configuration from files"""
        self._load_categories()
        self._load_modules()
        self._load_templates()
    
    def _load_categories(self):
        """Load categories from categories.yaml"""
        categories_file = os.path.join(self.config_dir, "categories.yaml")
        
        if os.path.exists(categories_file):
            try:
                with open(categories_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                
                categories_data = data.get('categories', {})
                for name, config in categories_data.items():
                    self.categories[name] = CategoryConfig(
                        name=name,
                        description=config.get('description', ''),
                        icon=config.get('icon', '📄'),
                        subcategories=config.get('subcategories', []),
                        templates=config.get('templates', [])
                    )
            except Exception as e:
                print(f"Warning: Error loading categories config: {e}")
        
        # Ensure ai_insights category always exists
        if 'ai_insights' not in self.categories:
            self.categories['ai_insights'] = CategoryConfig(
                name='ai_insights',
                description='AI-generated insights and discoveries',
                icon='🧠',
                subcategories=['learned_patterns', 'user_preferences', 'discoveries'],
                templates=['insight', 'pattern', 'discovery']
            )
    
    def _load_modules(self):
        """Load modules from modules.yaml"""
        modules_file = os.path.join(self.config_dir, "modules.yaml")
        
        if os.path.exists(modules_file):
            try:
                with open(modules_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                
                modules_data = data.get('modules', {})
                for name, config in modules_data.items():
                    self.modules[name] = ModuleConfig(
                        name=name,
                        enabled=config.get('enabled', True),
                        class_name=config.get('class', ''),
                        config=config.get('config', {})
                    )
            except Exception as e:
                print(f"Warning: Error loading modules config: {e}")
        
        # Add default modules if none exist
        if not self.modules:
            self._add_default_modules()
    
    def _load_templates(self):
        """Load templates from templates.yaml"""
        templates_file = os.path.join(self.config_dir, "templates.yaml")
        
        if os.path.exists(templates_file):
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                
                self.default_templates = data.get('default_templates', {})
            except Exception as e:
                print(f"Warning: Error loading templates config: {e}")
    
    def _add_default_modules(self):
        """Add default knowledge modules"""
        default_modules = {
            'document_knowledge': ModuleConfig(
                name='document_knowledge',
                enabled=True,
                class_name='DocumentKnowledgeModule',
                config={
                    'auto_summarize': True,
                    'extract_headings': True,
                    'supported_formats': ['md', 'txt', 'pdf']
                }
            ),
            'code_knowledge': ModuleConfig(
                name='code_knowledge',
                enabled=False,  # Disabled by default
                class_name='CodeKnowledgeModule',
                config={
                    'syntax_highlighting': True,
                    'auto_extract_functions': True,
                    'supported_languages': ['python', 'javascript', 'go', 'rust']
                }
            )
        }
        
        self.modules.update(default_modules)
    
    def save_config(self):
        """Save configuration to files"""
        self._save_categories()
        self._save_modules()
        self._save_templates()
    
    def _save_categories(self):
        """Save categories to categories.yaml"""
        categories_file = os.path.join(self.config_dir, "categories.yaml")
        
        data = {
            'categories': {
                name: config.to_dict() 
                for name, config in self.categories.items()
            }
        }
        
        with open(categories_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    def _save_modules(self):
        """Save modules to modules.yaml"""
        modules_file = os.path.join(self.config_dir, "modules.yaml")
        
        data = {
            'modules': {
                name: config.to_dict()
                for name, config in self.modules.items()
            }
        }
        
        with open(modules_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    def _save_templates(self):
        """Save templates to templates.yaml"""
        templates_file = os.path.join(self.config_dir, "templates.yaml")
        
        data = {
            'default_templates': self.default_templates
        }
        
        with open(templates_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    def add_category(self, name: str, description: str = "", icon: str = "📄", 
                     subcategories: List[str] = None, templates: List[str] = None):
        """Add a new category"""
        self.categories[name] = CategoryConfig(
            name=name,
            description=description,
            icon=icon,
            subcategories=subcategories or [],
            templates=templates or []
        )
        
        # Create directory for category
        category_dir = os.path.join(self.knowledge_dir, name)
        os.makedirs(category_dir, exist_ok=True)
        
        # Create subdirectories
        for subcat in (subcategories or []):
            subcat_dir = os.path.join(category_dir, subcat)
            os.makedirs(subcat_dir, exist_ok=True)
        
        self._save_categories()
    
    def remove_category(self, name: str):
        """Remove a category"""
        if name in self.categories:
            del self.categories[name]
            self._save_categories()
    
    def enable_module(self, name: str):
        """Enable a knowledge module"""
        if name in self.modules:
            self.modules[name].enabled = True
            self._save_modules()
    
    def disable_module(self, name: str):
        """Disable a knowledge module"""
        if name in self.modules:
            self.modules[name].enabled = False
            self._save_modules()
    
    def get_enabled_modules(self) -> List[str]:
        """Get list of enabled module names"""
        return [name for name, config in self.modules.items() if config.enabled]
    
    def get_category_path(self, category: str, subcategory: str = None) -> str:
        """Get the file system path for a category"""
        path = os.path.join(self.knowledge_dir, category)
        if subcategory:
            path = os.path.join(path, subcategory)
        return path
    
    def init_from_preset(self, preset_name: str):
        """Initialize knowledge base from a preset"""
        presets = {
            'developer': self._get_developer_preset(),
            'personal': self._get_personal_preset(),
            'business': self._get_business_preset(),
            'academic': self._get_academic_preset()
        }
        
        preset = presets.get(preset_name)
        if not preset:
            raise ValueError(f"Unknown preset: {preset_name}")
        
        # Add categories from preset
        for name, config in preset['categories'].items():
            self.add_category(
                name=name,
                description=config['description'],
                icon=config['icon'],
                subcategories=config['subcategories'],
                templates=config['templates']
            )
        
        # Enable modules from preset
        for module_name in preset.get('modules', []):
            if module_name in self.modules:
                self.enable_module(module_name)
        
        # Set default templates
        self.default_templates.update(preset.get('default_templates', {}))
        self._save_templates()
    
    def _get_developer_preset(self) -> Dict[str, Any]:
        """Get developer preset configuration"""
        return {
            'categories': {
                'coding': {
                    'description': 'Programming knowledge and code snippets',
                    'icon': '💻',
                    'subcategories': ['python', 'javascript', 'algorithms', 'patterns'],
                    'templates': ['code_snippet', 'library_notes', 'bug_fix']
                },
                'projects': {
                    'description': 'Development projects and documentation',
                    'icon': '🚀',
                    'subcategories': ['active', 'completed', 'ideas'],
                    'templates': ['project_doc', 'architecture', 'deployment']
                },
                'documentation': {
                    'description': 'Technical documentation and guides',
                    'icon': '📚',
                    'subcategories': ['api', 'tutorials', 'guides'],
                    'templates': ['api_doc', 'tutorial', 'troubleshooting']
                },
                'tools': {
                    'description': 'Development tools and configurations',
                    'icon': '🛠️',
                    'subcategories': ['cli', 'editors', 'libraries'],
                    'templates': ['tool_review', 'configuration', 'tips']
                }
            },
            'modules': ['code_knowledge', 'document_knowledge'],
            'default_templates': {
                'coding': 'code_snippet',
                'projects': 'project_doc',
                'documentation': 'api_doc'
            }
        }
    
    def _get_personal_preset(self) -> Dict[str, Any]:
        """Get personal preset configuration"""
        return {
            'categories': {
                'journal': {
                    'description': 'Personal journal and reflections',
                    'icon': '📔',
                    'subcategories': ['daily', 'weekly', 'monthly'],
                    'templates': ['journal_entry', 'reflection', 'gratitude']
                },
                'goals': {
                    'description': 'Personal and professional goals',
                    'icon': '🎯',
                    'subcategories': ['short_term', 'long_term', 'completed'],
                    'templates': ['goal', 'milestone', 'review']
                },
                'learning': {
                    'description': 'Learning notes and progress',
                    'icon': '📖',
                    'subcategories': ['courses', 'books', 'skills'],
                    'templates': ['course_notes', 'book_summary', 'skill_practice']
                },
                'ideas': {
                    'description': 'Creative ideas and inspiration',
                    'icon': '💡',
                    'subcategories': ['projects', 'writing', 'business'],
                    'templates': ['idea', 'brainstorm', 'concept']
                }
            },
            'modules': ['document_knowledge'],
            'default_templates': {
                'journal': 'journal_entry',
                'goals': 'goal',
                'learning': 'course_notes',
                'ideas': 'idea'
            }
        }
    
    def _get_business_preset(self) -> Dict[str, Any]:
        """Get business preset configuration"""
        return {
            'categories': {
                'company': {
                    'description': 'Company information and policies',
                    'icon': '🏢',
                    'subcategories': ['policies', 'procedures', 'culture'],
                    'templates': ['policy', 'procedure', 'announcement']
                },
                'projects': {
                    'description': 'Business projects and initiatives',
                    'icon': '📊',
                    'subcategories': ['active', 'completed', 'planning'],
                    'templates': ['project_brief', 'status_report', 'proposal']
                },
                'meetings': {
                    'description': 'Meeting notes and action items',
                    'icon': '🤝',
                    'subcategories': ['team', 'client', 'board'],
                    'templates': ['meeting_notes', 'action_items', 'agenda']
                },
                'contacts': {
                    'description': 'Business contacts and relationships',
                    'icon': '👥',
                    'subcategories': ['clients', 'partners', 'vendors'],
                    'templates': ['contact_info', 'relationship_notes', 'communication_log']
                }
            },
            'modules': ['document_knowledge'],
            'default_templates': {
                'company': 'policy',
                'projects': 'project_brief',
                'meetings': 'meeting_notes',
                'contacts': 'contact_info'
            }
        }
    
    def _get_academic_preset(self) -> Dict[str, Any]:
        """Get academic preset configuration"""
        return {
            'categories': {
                'research': {
                    'description': 'Research projects and findings',
                    'icon': '🔬',
                    'subcategories': ['active', 'completed', 'ideas'],
                    'templates': ['research_notes', 'hypothesis', 'findings']
                },
                'papers': {
                    'description': 'Academic papers and publications',
                    'icon': '📄',
                    'subcategories': ['published', 'drafts', 'reviews'],
                    'templates': ['paper_summary', 'literature_review', 'citation']
                },
                'courses': {
                    'description': 'Course materials and notes',
                    'icon': '🎓',
                    'subcategories': ['current', 'completed', 'teaching'],
                    'templates': ['lecture_notes', 'assignment', 'syllabus']
                },
                'references': {
                    'description': 'Reference materials and citations',
                    'icon': '📚',
                    'subcategories': ['books', 'articles', 'datasets'],
                    'templates': ['reference', 'annotation', 'bibliography']
                }
            },
            'modules': ['document_knowledge'],
            'default_templates': {
                'research': 'research_notes',
                'papers': 'paper_summary',
                'courses': 'lecture_notes',
                'references': 'reference'
            }
        }
    
    def _get_coding_preset(self) -> Dict[str, Any]:
        """Get coding preset configuration"""
        return {
            'categories': {
                'programming': {
                    'description': 'Programming concepts and techniques',
                    'icon': '💻',
                    'subcategories': ['algorithms', 'data-structures', 'design-patterns'],
                    'templates': ['code_snippet', 'algorithm', 'pattern']
                },
                'python': {
                    'description': 'Python-specific knowledge',
                    'icon': '🐍',
                    'subcategories': ['basics', 'advanced', 'libraries'],
                    'templates': ['python_snippet', 'library_usage', 'best_practice']
                },
                'web-development': {
                    'description': 'Web development frameworks and tools',
                    'icon': '🌐',
                    'subcategories': ['frontend', 'backend', 'fullstack'],
                    'templates': ['framework_guide', 'api_example', 'deployment']
                },
                'database': {
                    'description': 'Database design and queries',
                    'icon': '🗄️',
                    'subcategories': ['sql', 'nosql', 'optimization'],
                    'templates': ['query_example', 'schema_design', 'performance_tip']
                },
                'devops': {
                    'description': 'DevOps tools and practices',
                    'icon': '⚙️',
                    'subcategories': ['ci-cd', 'containers', 'monitoring'],
                    'templates': ['deployment_guide', 'config_example', 'troubleshooting']
                }
            },
            'modules': ['code_knowledge', 'document_knowledge'],
            'default_templates': {
                'programming': 'code_snippet',
                'python': 'python_snippet',
                'web-development': 'framework_guide',
                'database': 'query_example',
                'devops': 'deployment_guide'
            }
        }
    
    def apply_preset(self, preset_name: str):
        """Apply a preset configuration"""
        preset_methods = {
            'personal': self._get_personal_preset,
            'business': self._get_business_preset,
            'academic': self._get_academic_preset,
            'coding': self._get_coding_preset
        }
        
        if preset_name not in preset_methods:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(preset_methods.keys())}")
        
        preset_config = preset_methods[preset_name]()
        
        # Apply categories
        if 'categories' in preset_config:
            for cat_name, cat_config in preset_config['categories'].items():
                self.add_category(
                    name=cat_name,
                    description=cat_config.get('description', ''),
                    icon=cat_config.get('icon', '📄'),
                    subcategories=cat_config.get('subcategories', []),
                    templates=cat_config.get('templates', [])
                )
        
        # Apply default templates
        if 'default_templates' in preset_config:
            self.default_templates.update(preset_config['default_templates'])
        
        # Enable modules
        if 'modules' in preset_config:
            for module_name in preset_config['modules']:
                if module_name not in self.modules:
                    self.modules[module_name] = ModuleConfig(
                        name=module_name,
                        enabled=True,
                        config={}
                    )
                else:
                    self.modules[module_name].enabled = True
    
    def get_enabled_modules(self) -> List[str]:
        """Get list of enabled module names"""
        return [name for name, config in self.modules.items() if config.enabled]
