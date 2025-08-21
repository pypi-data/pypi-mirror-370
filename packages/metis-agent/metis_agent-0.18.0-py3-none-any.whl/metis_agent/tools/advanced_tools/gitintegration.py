from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import os
import re
import time
import subprocess
import json
from collections import defaultdict, Counter
from pathlib import Path
from ..base import BaseTool

class GitIntegrationTool(BaseTool):
    """Production-ready Git integration tool with intelligent version control operations.
    
    This tool provides comprehensive Git operations including status analysis,
    commit message generation, branch management, history analysis, code review
    assistance, and repository insights with intelligent automation.
    """
    
    def __init__(self):
        """Initialize Git integration tool with required attributes."""
        # Required attributes
        self.name = "GitIntegrationTool"
        self.description = "Comprehensive Git version control operations including status analysis, commit generation, branch management, and code review"
        
        # Optional metadata
        self.version = "2.0.0"
        self.category = "advanced_tools"
        
        # Git operation types and their characteristics
        self.git_operations = {
            'status': {
                'keywords': ['status', 'state', 'changes', 'modified', 'staged', 'unstaged'],
                'commands': ['status', 'diff --name-only', 'ls-files --others --exclude-standard'],
                'analysis': ['file_changes', 'staging_area', 'working_directory']
            },
            'history': {
                'keywords': ['history', 'log', 'commits', 'timeline', 'past', 'changelog'],
                'commands': ['log', 'show', 'reflog'],
                'analysis': ['commit_patterns', 'author_analysis', 'frequency']
            },
            'commit': {
                'keywords': ['commit', 'save', 'record', 'checkpoint', 'message'],
                'commands': ['commit', 'add', 'reset'],
                'analysis': ['staged_files', 'message_generation', 'commit_quality']
            },
            'branch': {
                'keywords': ['branch', 'switch', 'checkout', 'create', 'merge', 'feature'],
                'commands': ['branch', 'checkout', 'merge', 'rebase'],
                'analysis': ['branch_structure', 'merge_conflicts', 'divergence']
            },
            'diff': {
                'keywords': ['diff', 'difference', 'changes', 'compare', 'delta'],
                'commands': ['diff', 'show', 'difftool'],
                'analysis': ['change_analysis', 'line_counts', 'file_impact']
            },
            'remote': {
                'keywords': ['remote', 'push', 'pull', 'fetch', 'origin', 'upstream'],
                'commands': ['remote', 'push', 'pull', 'fetch'],
                'analysis': ['sync_status', 'remote_tracking', 'conflicts']
            },
            'review': {
                'keywords': ['review', 'analyze', 'check', 'audit', 'quality'],
                'commands': ['diff', 'log', 'blame'],
                'analysis': ['code_quality', 'review_points', 'change_complexity']
            }
        }
        
        # Git command operation types
        self.operation_types = {
            'analyze': ['analyze', 'check', 'review', 'examine', 'inspect'],
            'create': ['create', 'add', 'new', 'initialize', 'setup'],
            'modify': ['modify', 'change', 'update', 'edit', 'alter'],
            'navigate': ['switch', 'checkout', 'go to', 'move to'],
            'manage': ['manage', 'organize', 'maintain', 'handle'],
            'generate': ['generate', 'create', 'produce', 'make', 'build']
        }
        
        # Git file status mapping
        self.status_mapping = {
            'A': 'Added',
            'M': 'Modified', 
            'D': 'Deleted',
            'R': 'Renamed',
            'C': 'Copied',
            'U': 'Unmerged',
            '?': 'Untracked',
            '!': 'Ignored'
        }
        
        # Commit message templates
        self.commit_templates = {
            'feature': 'feat: {description}',
            'fix': 'fix: {description}',
            'docs': 'docs: {description}',
            'style': 'style: {description}',
            'refactor': 'refactor: {description}',
            'test': 'test: {description}',
            'chore': 'chore: {description}'
        }
        
        # Repository analysis cache
        self.analysis_cache = {}
        self.cache_timeout = 300  # 5 minutes
        
        # Command execution settings
        self.command_timeout = 30
        self.max_log_entries = 50
    
    def can_handle(self, task: str) -> bool:
        """Intelligent Git operation task detection.
        
        Uses multi-layer analysis to determine if a task requires
        Git version control capabilities.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires Git operations, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_lower = task.strip().lower()
        
        # Layer 1: Direct Git Keywords
        git_keywords = {
            'git', 'repository', 'repo', 'version control', 'vcs',
            'commit', 'branch', 'merge', 'pull', 'push', 'clone'
        }
        
        if any(keyword in task_lower for keyword in git_keywords):
            return True
        
        # Layer 2: Git Operation Detection (more specific)
        # Early exclusion for clearly non-Git tasks
        non_git_patterns = [
            r'\b(weather|temperature|cooking|recipe|translate|language|currency)\b',
            r'\b(music|play|book|flight|email|send|calculate|math)\b',
            r'\b(powerpoint|presentation|excel|word|document)\b',
            r'\b(pasta|food|eat|drink|restaurant)\b'
        ]
        
        if any(re.search(pattern, task_lower) for pattern in non_git_patterns):
            return False
        
        # More specific Git operation patterns
        git_operation_patterns = [
            r'\b(git\s+status|repository\s+status|repo\s+status)\b',
            r'\b(git\s+log|commit\s+history|git\s+history)\b',
            r'\b(git\s+branch|switch\s+branch|checkout\s+branch)\b',
            r'\b(git\s+diff|show\s+diff|compare\s+changes)\b',
            r'\b(git\s+add|stage\s+files|git\s+commit)\b',
            r'\b(git\s+push|git\s+pull|git\s+fetch)\b'
        ]
        
        if any(re.search(pattern, task_lower) for pattern in git_operation_patterns):
            return True
        
        # Check for Git-specific keywords in context with word boundaries
        for operation, info in self.git_operations.items():
            for keyword in info['keywords']:
                # Use word boundaries for precise matching
                if re.search(r'\b' + re.escape(keyword) + r'\b', task_lower):
                    # Additional context check for ambiguous keywords
                    if keyword in ['create', 'changes', 'state', 'history', 'log']:
                        # Require Git context for ambiguous keywords
                        git_context = ['git', 'repository', 'repo', 'commit', 'branch']
                        if any(ctx in task_lower for ctx in git_context):
                            return True
                    else:
                        return True
        
        # Layer 3: Version Control Concepts
        vc_concepts = {
            'staged', 'unstaged', 'working directory', 'staging area',
            'HEAD', 'origin', 'upstream', 'master', 'main', 'develop'
        }
        
        if any(concept in task_lower for concept in vc_concepts):
            return True
        
        # Layer 4: File Management in Git Context
        file_management_patterns = [
            r'track\s+(files|changes)',
            r'stage\s+(files|changes)',
            r'commit\s+(files|changes)',
            r'revert\s+(files|changes)',
            r'checkout\s+\w+',
            r'merge\s+\w+'
        ]
        
        if any(re.search(pattern, task_lower) for pattern in file_management_patterns):
            return True
        
        # Layer 5: Development Workflow Indicators
        workflow_indicators = {
            'feature branch', 'pull request', 'merge request',
            'code review', 'conflict resolution', 'cherry-pick',
            'rebase', 'squash', 'amend'
        }
        
        if any(indicator in task_lower for indicator in workflow_indicators):
            return True
        
        # Layer 6: Repository State Queries
        state_queries = [
            r'what\s+(changed|modified)',
            r'show\s+(status|changes|history)',
            r'list\s+(branches|commits)',
            r'check\s+(repository|repo|git)',
            r'current\s+branch'
        ]
        
        if any(re.search(query, task_lower) for query in state_queries):
            return True
        
        # Layer 7: Exclusion Rules
        non_git_indicators = {
            'weather', 'temperature', 'cooking', 'recipe',
            'translate', 'language', 'currency', 'math problem'
        }
        
        if any(indicator in task_lower for indicator in non_git_indicators):
            # Only exclude if it's clearly not Git-related
            git_indicators = {'git', 'commit', 'branch', 'repository'}
            if not any(indicator in task_lower for indicator in git_indicators):
                return False
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute Git operations with robust error handling.
        
        Args:
            task: Git operation task to perform
            **kwargs: Additional parameters (cwd, branch_name, commit_message, etc.)
            
        Returns:
            Structured dictionary with Git operation results
        """
        start_time = time.time()
        
        try:
            # Input validation
            if not task or not isinstance(task, str):
                return self._error_response("Task must be a non-empty string")
            
            if not self.can_handle(task):
                return self._error_response("Task does not appear to be Git-related")
            
            # Get working directory
            cwd = kwargs.get('cwd', os.getcwd())
            
            # Validate Git repository
            if not self._is_git_repository(cwd):
                return self._error_response("Not in a Git repository", suggestions=[
                    "Initialize repository with: git init",
                    "Clone an existing repository",
                    "Navigate to a Git repository directory"
                ])
            
            # Detect Git operation and parameters
            operation = self._detect_git_operation(task)
            operation_type = self._detect_operation_type(task)
            
            # Execute Git operation
            result = self._execute_git_operation(operation, operation_type, task, cwd, kwargs)
            
            if not result or not result.get('success'):
                return self._error_response("Git operation failed")
            
            execution_time = time.time() - start_time
            
            # Generate comprehensive Git report
            git_report = {
                'operation_info': {
                    'operation': operation,
                    'operation_type': operation_type,
                    'repository_path': cwd,
                    'execution_status': 'success'
                },
                'git_data': result['data'],
                'repository_analysis': result.get('analysis', {}),
                'insights': result.get('insights', []),
                'recommendations': result.get('recommendations', []),
                'next_steps': result.get('next_steps', []),
                'quality_assessment': self._assess_operation_quality(result)
            }
            
            # Success response
            return {
                'success': True,
                'result': git_report,
                'message': f"Git {operation} operation completed successfully",
                'metadata': {
                    'tool_name': self.name,
                    'execution_time': execution_time,
                    'task_type': 'git_operation',
                    'operation': operation,
                    'operation_type': operation_type,
                    'repository_path': cwd,
                    'has_changes': result.get('has_changes', False),
                    'files_affected': result.get('files_count', 0)
                }
            }
            
        except Exception as e:
            return self._error_response(f"Git operation failed: {str(e)}", e)
    
    def _detect_git_operation(self, task: str) -> str:
        """Detect the specific Git operation to perform."""
        task_lower = task.lower()
        
        # Score each operation based on keyword matches with priority weighting
        scores = {}
        for operation, info in self.git_operations.items():
            score = 0
            for keyword in info['keywords']:
                # Use word boundaries for more precise matching
                import re
                # Check exact match
                if re.search(r'\b' + re.escape(keyword) + r'\b', task_lower):
                    # Give higher score for exact operation name matches
                    if keyword == operation:
                        score += 3
                    # Give higher score for primary keywords
                    elif keyword in ['commit', 'status', 'branch', 'history', 'diff', 'remote', 'review']:
                        score += 2
                    else:
                        score += 1
                # Check plural forms for key nouns
                elif keyword in ['difference', 'remote', 'branch', 'change'] and re.search(r'\b' + re.escape(keyword) + r's\b', task_lower):
                    # Give score for plural matches
                    if keyword == operation or keyword in ['diff', 'remote']:
                        score += 2
                    else:
                        score += 1
            scores[operation] = score
        
        # Return highest scoring operation
        if scores and max(scores.values()) > 0:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        # Default based on common patterns with word boundaries
        import re
        if re.search(r'\b(status|state|current)\b', task_lower):
            return 'status'
        elif re.search(r'\b(history|log|past)\b', task_lower):
            return 'history'
        elif re.search(r'\b(branch|switch)\b', task_lower):
            return 'branch'
        else:
            return 'status'  # Default
    
    def _detect_operation_type(self, task: str) -> str:
        """Detect the type of operation to perform."""
        task_lower = task.lower()
        
        for op_type, keywords in self.operation_types.items():
            if any(keyword in task_lower for keyword in keywords):
                return op_type
        
        return 'analyze'  # Default operation type
    
    def _is_git_repository(self, cwd: str) -> bool:
        """Check if the current directory is a Git repository."""
        try:
            result = self._run_git_command(['rev-parse', '--git-dir'], cwd)
            return result.returncode == 0
        except Exception:
            return False
    
    def _run_git_command(self, cmd: List[str], cwd: str) -> subprocess.CompletedProcess:
        """Run a Git command safely with error handling."""
        try:
            return subprocess.run(
                ['git'] + cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace invalid characters instead of failing
                timeout=self.command_timeout
            )
        except subprocess.TimeoutExpired:
            raise Exception(f"Git command timed out: git {' '.join(cmd)}")
        except UnicodeDecodeError as e:
            # Fallback: try with different encoding strategies
            try:
                result = subprocess.run(
                    ['git'] + cmd,
                    cwd=cwd,
                    capture_output=True,
                    text=False,  # Get bytes instead
                    timeout=self.command_timeout
                )
                # Try to decode with multiple encodings
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        stdout = result.stdout.decode(encoding, errors='replace')
                        stderr = result.stderr.decode(encoding, errors='replace')
                        # Create a new CompletedProcess with decoded strings
                        return subprocess.CompletedProcess(
                            result.args, result.returncode, stdout, stderr
                        )
                    except UnicodeDecodeError:
                        continue
                # If all encodings fail, use replace errors
                stdout = result.stdout.decode('utf-8', errors='replace')
                stderr = result.stderr.decode('utf-8', errors='replace')
                return subprocess.CompletedProcess(
                    result.args, result.returncode, stdout, stderr
                )
            except Exception as fallback_e:
                raise Exception(f"Git command failed with encoding issues: {str(fallback_e)}")
        except Exception as e:
            raise Exception(f"Git command failed: {str(e)}")
    
    def _execute_git_operation(self, operation: str, operation_type: str, task: str, 
                              cwd: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specific Git operation."""
        
        if operation == 'status':
            return self._handle_status_operation(cwd, operation_type, kwargs)
        elif operation == 'history':
            return self._handle_history_operation(cwd, operation_type, kwargs)
        elif operation == 'commit':
            return self._handle_commit_operation(cwd, operation_type, task, kwargs)
        elif operation == 'branch':
            return self._handle_branch_operation(cwd, operation_type, task, kwargs)
        elif operation == 'diff':
            return self._handle_diff_operation(cwd, operation_type, kwargs)
        elif operation == 'remote':
            return self._handle_remote_operation(cwd, operation_type, kwargs)
        elif operation == 'review':
            return self._handle_review_operation(cwd, operation_type, kwargs)
        else:
            return self._handle_status_operation(cwd, operation_type, kwargs)  # Default
    
    def _handle_status_operation(self, cwd: str, operation_type: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Git status operations."""
        try:
            # Get porcelain status
            status_result = self._run_git_command(['status', '--porcelain'], cwd)
            if status_result.returncode != 0:
                return {'success': False, 'error': status_result.stderr}
            
            # Parse status output
            staged_files = []
            unstaged_files = []
            untracked_files = []
            
            for line in status_result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                status_codes = line[:2]
                filename = line[3:].strip()
                
                # Staged changes
                if status_codes[0] != ' ' and status_codes[0] != '?':
                    staged_files.append({
                        'file': filename,
                        'status': self.status_mapping.get(status_codes[0], 'Unknown'),
                        'status_code': status_codes[0]
                    })
                
                # Unstaged changes
                if status_codes[1] != ' ':
                    unstaged_files.append({
                        'file': filename,
                        'status': self.status_mapping.get(status_codes[1], 'Unknown'),
                        'status_code': status_codes[1]
                    })
                
                # Untracked files
                if status_codes == '??':
                    untracked_files.append(filename)
            
            # Get current branch
            branch_result = self._run_git_command(['branch', '--show-current'], cwd)
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else 'unknown'
            
            # Get repository statistics
            stats = self._get_repository_stats(cwd)
            
            # Generate insights
            insights = self._generate_status_insights(staged_files, unstaged_files, untracked_files, stats)
            
            # Generate recommendations
            recommendations = self._generate_status_recommendations(staged_files, unstaged_files, untracked_files)
            
            return {
                'success': True,
                'data': {
                    'current_branch': current_branch,
                    'staged_files': staged_files,
                    'unstaged_files': unstaged_files,
                    'untracked_files': untracked_files,
                    'repository_stats': stats
                },
                'analysis': {
                    'total_changes': len(staged_files) + len(unstaged_files),
                    'ready_to_commit': len(staged_files) > 0 and len(unstaged_files) == 0,
                    'has_untracked': len(untracked_files) > 0,
                    'repository_state': self._assess_repository_state(staged_files, unstaged_files, untracked_files)
                },
                'insights': insights,
                'recommendations': recommendations,
                'has_changes': len(staged_files) + len(unstaged_files) > 0,
                'files_count': len(staged_files) + len(unstaged_files) + len(untracked_files)
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Status operation failed: {str(e)}"}
    
    def _handle_history_operation(self, cwd: str, operation_type: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Git history operations."""
        try:
            # Get commit history
            limit = kwargs.get('limit', self.max_log_entries)
            log_result = self._run_git_command([
                'log', f'--max-count={limit}', '--pretty=format:%H|%an|%ae|%ad|%s|%p',
                '--date=iso'
            ], cwd)
            
            if log_result.returncode != 0:
                return {'success': False, 'error': log_result.stderr}
            
            commits = []
            for line in log_result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 5:
                        commits.append({
                            'hash': parts[0][:8],  # Short hash
                            'full_hash': parts[0],
                            'author_name': parts[1],
                            'author_email': parts[2],
                            'date': parts[3],
                            'message': parts[4],
                            'parents': parts[5].split() if len(parts) > 5 else []
                        })
            
            # Analyze commit patterns
            analysis = self._analyze_commit_history(commits)
            
            # Generate insights
            insights = self._generate_history_insights(commits, analysis)
            
            return {
                'success': True,
                'data': {
                    'commits': commits,
                    'total_commits': len(commits),
                    'commit_analysis': analysis
                },
                'analysis': analysis,
                'insights': insights,
                'files_count': len(commits)
            }
            
        except Exception as e:
            return {'success': False, 'error': f"History operation failed: {str(e)}"}
    
    def _handle_commit_operation(self, cwd: str, operation_type: str, task: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Git commit operations."""
        try:
            # Get staged changes
            staged_result = self._run_git_command(['diff', '--cached', '--name-status'], cwd)
            if staged_result.returncode != 0:
                return {'success': False, 'error': 'No staged changes found'}
            
            staged_changes = []
            for line in staged_result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t', 1)
                    if len(parts) == 2:
                        status, filename = parts
                        staged_changes.append({
                            'status': self.status_mapping.get(status, 'Unknown'),
                            'status_code': status,
                            'file': filename,
                            'extension': Path(filename).suffix
                        })
            
            if not staged_changes:
                return {'success': False, 'error': 'No staged changes to commit'}
            
            # Generate commit message if requested
            commit_message = None
            if operation_type == 'generate' or 'message' in task.lower():
                commit_message = self._generate_commit_message(staged_changes)
            
            # Analyze commit quality
            commit_analysis = self._analyze_commit_quality(staged_changes)
            
            return {
                'success': True,
                'data': {
                    'staged_changes': staged_changes,
                    'suggested_message': commit_message,
                    'commit_analysis': commit_analysis
                },
                'analysis': commit_analysis,
                'insights': [
                    f"Ready to commit {len(staged_changes)} file(s)",
                    f"Changes affect {len(set(c['extension'] for c in staged_changes))} file type(s)"
                ],
                'recommendations': [
                    f"Use: git commit -m \"{commit_message}\"" if commit_message else "Stage changes first with: git add <files>",
                    "Review changes with: git diff --cached"
                ],
                'files_count': len(staged_changes)
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Commit operation failed: {str(e)}"}
    
    def _handle_branch_operation(self, cwd: str, operation_type: str, task: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Git branch operations."""
        try:
            # Get all branches
            branch_result = self._run_git_command(['branch', '-a'], cwd)
            if branch_result.returncode != 0:
                return {'success': False, 'error': branch_result.stderr}
            
            branches = []
            current_branch = None
            
            for line in branch_result.stdout.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('* '):
                    current_branch = line[2:]
                    branches.append({
                        'name': current_branch,
                        'current': True,
                        'type': 'local'
                    })
                elif line.startswith('remotes/'):
                    remote_branch = line[8:]  # Remove 'remotes/'
                    if ' -> ' not in remote_branch:  # Skip symbolic refs
                        branches.append({
                            'name': remote_branch,
                            'current': False,
                            'type': 'remote'
                        })
                else:
                    branches.append({
                        'name': line,
                        'current': False,
                        'type': 'local'
                    })
            
            # Branch analysis
            local_branches = [b for b in branches if b['type'] == 'local']
            remote_branches = [b for b in branches if b['type'] == 'remote']
            
            # Handle specific branch operations
            next_steps = []
            if operation_type == 'create' and 'branch' in task.lower():
                next_steps.append("Specify branch name to create")
            elif operation_type == 'navigate' and ('switch' in task.lower() or 'checkout' in task.lower()):
                next_steps.append("Specify branch name to switch to")
            
            return {
                'success': True,
                'data': {
                    'current_branch': current_branch,
                    'branches': branches,
                    'local_branches': local_branches,
                    'remote_branches': remote_branches
                },
                'analysis': {
                    'total_branches': len(branches),
                    'local_count': len(local_branches),
                    'remote_count': len(remote_branches),
                    'branch_complexity': 'Simple' if len(local_branches) <= 3 else 'Complex'
                },
                'insights': [
                    f"Currently on branch '{current_branch}'",
                    f"Repository has {len(local_branches)} local branch(es)",
                    f"Tracking {len(remote_branches)} remote branch(es)"
                ],
                'next_steps': next_steps,
                'files_count': len(branches)
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Branch operation failed: {str(e)}"}
    
    def _handle_diff_operation(self, cwd: str, operation_type: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Git diff operations."""
        try:
            # Get diff statistics
            diff_result = self._run_git_command(['diff', '--stat'], cwd)
            if diff_result.returncode != 0:
                return {'success': False, 'error': diff_result.stderr}
            
            # Parse diff statistics
            diff_lines = diff_result.stdout.strip().split('\n')
            file_changes = []
            total_insertions = 0
            total_deletions = 0
            
            for line in diff_lines[:-1]:  # Skip summary line
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) == 2:
                        filename = parts[0].strip()
                        changes = parts[1].strip()
                        
                        # Parse insertions and deletions
                        insertions = changes.count('+')
                        deletions = changes.count('-')
                        
                        file_changes.append({
                            'file': filename,
                            'insertions': insertions,
                            'deletions': deletions,
                            'total_changes': insertions + deletions
                        })
                        
                        total_insertions += insertions
                        total_deletions += deletions
            
            # Summary line analysis
            summary_line = diff_lines[-1] if diff_lines else ''
            files_changed = len(file_changes)
            
            return {
                'success': True,
                'data': {
                    'file_changes': file_changes,
                    'summary': {
                        'files_changed': files_changed,
                        'total_insertions': total_insertions,
                        'total_deletions': total_deletions,
                        'net_change': total_insertions - total_deletions
                    }
                },
                'analysis': {
                    'change_magnitude': 'Large' if total_insertions + total_deletions > 100 else 'Medium' if total_insertions + total_deletions > 10 else 'Small',
                    'change_type': 'Addition-heavy' if total_insertions > total_deletions * 2 else 'Deletion-heavy' if total_deletions > total_insertions * 2 else 'Balanced'
                },
                'insights': [
                    f"{files_changed} file(s) changed",
                    f"{total_insertions} insertion(s), {total_deletions} deletion(s)"
                ],
                'files_count': files_changed
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Diff operation failed: {str(e)}"}
    
    def _handle_remote_operation(self, cwd: str, operation_type: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Git remote operations."""
        try:
            # Get remote information
            remote_result = self._run_git_command(['remote', '-v'], cwd)
            if remote_result.returncode != 0:
                return {'success': False, 'error': remote_result.stderr}
            
            remotes = []
            for line in remote_result.stdout.strip().split('\n'):
                if line:
                    parts = line.split()
                    if len(parts) >= 3:
                        name, url, operation = parts[0], parts[1], parts[2].strip('()')
                        remotes.append({
                            'name': name,
                            'url': url,
                            'operation': operation
                        })
            
            # Get tracking branch information
            tracking_result = self._run_git_command(['status', '-b', '--porcelain'], cwd)
            tracking_info = {}
            
            if tracking_result.returncode == 0:
                first_line = tracking_result.stdout.split('\n')[0]
                if 'ahead' in first_line or 'behind' in first_line:
                    tracking_info['sync_status'] = first_line
                else:
                    tracking_info['sync_status'] = 'up to date'
            
            return {
                'success': True,
                'data': {
                    'remotes': remotes,
                    'tracking_info': tracking_info
                },
                'analysis': {
                    'remote_count': len(set(r['name'] for r in remotes)),
                    'has_origin': any(r['name'] == 'origin' for r in remotes),
                    'remote_configured': len(remotes) > 0
                },
                'insights': [
                    f"Repository has {len(set(r['name'] for r in remotes))} remote(s) configured",
                    "Origin remote found" if any(r['name'] == 'origin' for r in remotes) else "No origin remote configured"
                ],
                'files_count': len(remotes)
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Remote operation failed: {str(e)}"}
    
    def _handle_review_operation(self, cwd: str, operation_type: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Git code review operations."""
        try:
            # Get recent changes for review
            diff_result = self._run_git_command(['diff', 'HEAD~1'], cwd)
            if diff_result.returncode != 0:
                return {'success': False, 'error': 'No recent changes to review'}
            
            # Analyze the diff
            diff_output = diff_result.stdout
            added_lines = len([line for line in diff_output.split('\n') if line.startswith('+')])
            removed_lines = len([line for line in diff_output.split('\n') if line.startswith('-')])
            
            # Get changed files
            files_result = self._run_git_command(['diff', '--name-status', 'HEAD~1'], cwd)
            changed_files = []
            
            if files_result.returncode == 0:
                for line in files_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t', 1)
                        if len(parts) == 2:
                            status, filename = parts
                            changed_files.append({
                                'file': filename,
                                'status': self.status_mapping.get(status, 'Unknown'),
                                'extension': Path(filename).suffix
                            })
            
            # Generate review insights
            review_points = []
            if added_lines > removed_lines * 3:
                review_points.append("Large code addition - review for complexity and maintainability")
            if len(changed_files) > 10:
                review_points.append("Many files changed - ensure changes are cohesive")
            if any(f['extension'] in ['.py', '.js', '.java'] for f in changed_files):
                review_points.append("Code files modified - check for proper testing")
            
            return {
                'success': True,
                'data': {
                    'changed_files': changed_files,
                    'diff_stats': {
                        'lines_added': added_lines,
                        'lines_removed': removed_lines,
                        'net_change': added_lines - removed_lines
                    },
                    'review_points': review_points
                },
                'analysis': {
                    'change_complexity': 'High' if len(changed_files) > 5 else 'Medium' if len(changed_files) > 2 else 'Low',
                    'review_priority': 'High' if added_lines > 100 else 'Medium' if added_lines > 20 else 'Low'
                },
                'insights': [
                    f"{len(changed_files)} file(s) changed in recent commit",
                    f"Net change: +{added_lines - removed_lines} lines"
                ],
                'recommendations': review_points if review_points else ["Changes look reasonable for review"],
                'files_count': len(changed_files)
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Review operation failed: {str(e)}"}
    
    def _get_repository_stats(self, cwd: str) -> Dict[str, Any]:
        """Get general repository statistics."""
        stats = {}
        
        try:
            # Total commits
            commit_count = self._run_git_command(['rev-list', '--count', 'HEAD'], cwd)
            if commit_count.returncode == 0:
                stats['total_commits'] = int(commit_count.stdout.strip())
            
            # Contributors
            contributors = self._run_git_command(['shortlog', '-sn'], cwd)
            if contributors.returncode == 0:
                stats['contributors'] = len(contributors.stdout.strip().split('\n'))
            
            # Repository age
            first_commit = self._run_git_command(['log', '--reverse', '--format=%ad', '--date=short', '-1'], cwd)
            if first_commit.returncode == 0:
                stats['first_commit_date'] = first_commit.stdout.strip()
                
        except Exception:
            pass  # Stats are optional
        
        return stats
    
    def _generate_status_insights(self, staged: List[Dict], unstaged: List[Dict], 
                                untracked: List[str], stats: Dict[str, Any]) -> List[str]:
        """Generate insights about repository status."""
        insights = []
        
        total_changes = len(staged) + len(unstaged)
        
        if total_changes == 0 and len(untracked) == 0:
            insights.append("Repository is clean - no changes detected")
        elif len(staged) > 0 and len(unstaged) == 0:
            insights.append(f"Ready to commit - {len(staged)} file(s) staged")
        elif len(unstaged) > 0:
            insights.append(f"Work in progress - {len(unstaged)} file(s) with unstaged changes")
        
        if len(untracked) > 0:
            insights.append(f"{len(untracked)} untracked file(s) found")
        
        # File type analysis
        all_files = [f['file'] for f in staged] + [f['file'] for f in unstaged] + untracked
        if all_files:
            extensions = [Path(f).suffix for f in all_files if Path(f).suffix]
            if extensions:
                most_common_ext = Counter(extensions).most_common(1)[0][0]
                insights.append(f"Most changes in {most_common_ext} files")
        
        return insights
    
    def _generate_status_recommendations(self, staged: List[Dict], unstaged: List[Dict], 
                                       untracked: List[str]) -> List[str]:
        """Generate recommendations based on status."""
        recommendations = []
        
        if len(unstaged) > 0:
            recommendations.append("Stage changes with: git add <file> or git add .")
        
        if len(staged) > 0:
            recommendations.append("Commit staged changes with: git commit -m \"message\"")
        
        if len(untracked) > 0:
            recommendations.append("Track new files with: git add <file>")
            
        if len(staged) == 0 and len(unstaged) == 0:
            recommendations.append("Repository is clean - start making changes")
        
        return recommendations
    
    def _analyze_commit_history(self, commits: List[Dict]) -> Dict[str, Any]:
        """Analyze commit history patterns."""
        if not commits:
            return {}
        
        # Author analysis
        authors = Counter(commit['author_name'] for commit in commits)
        
        # Message analysis
        messages = [commit['message'] for commit in commits]
        message_words = []
        for msg in messages:
            words = re.findall(r'\b\w+\b', msg.lower())
            message_words.extend(words)
        
        common_words = Counter(message_words).most_common(5)
        
        # Commit frequency
        dates = [commit['date'][:10] for commit in commits]  # Extract date part
        date_frequency = Counter(dates)
        
        return {
            'total_commits_analyzed': len(commits),
            'unique_authors': len(authors),
            'top_contributors': authors.most_common(3),
            'common_commit_words': common_words,
            'commit_frequency': len(date_frequency),
            'most_active_day': date_frequency.most_common(1)[0] if date_frequency else None
        }
    
    def _generate_history_insights(self, commits: List[Dict], analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from commit history."""
        insights = []
        
        if commits:
            insights.append(f"Analyzed {len(commits)} recent commit(s)")
            
            if analysis.get('unique_authors', 0) > 1:
                insights.append(f"Collaborative project with {analysis['unique_authors']} contributor(s)")
            
            if analysis.get('common_commit_words'):
                top_word = analysis['common_commit_words'][0][0]
                insights.append(f"Most common commit word: '{top_word}'")
            
            # Recent activity
            if len(commits) >= 5:
                insights.append("Active development - multiple recent commits")
            else:
                insights.append("Light recent activity")
        
        return insights
    
    def _generate_commit_message(self, staged_changes: List[Dict]) -> str:
        """Generate an intelligent commit message based on staged changes."""
        if not staged_changes:
            return "Update files"
        
        # Categorize changes by status
        added = [c for c in staged_changes if c['status'] == 'Added']
        modified = [c for c in staged_changes if c['status'] == 'Modified']
        deleted = [c for c in staged_changes if c['status'] == 'Deleted']
        
        # Analyze file types
        extensions = [c['extension'] for c in staged_changes if c['extension']]
        file_types = Counter(extensions)
        
        # Generate message parts
        parts = []
        
        if len(added) == 1:
            filename = Path(added[0]['file']).name
            parts.append(f"Add {filename}")
        elif len(added) > 1:
            parts.append(f"Add {len(added)} files")
        
        if len(modified) == 1:
            filename = Path(modified[0]['file']).name
            parts.append(f"Update {filename}")
        elif len(modified) > 1:
            parts.append(f"Update {len(modified)} files")
        
        if len(deleted) == 1:
            filename = Path(deleted[0]['file']).name
            parts.append(f"Remove {filename}")
        elif len(deleted) > 1:
            parts.append(f"Remove {len(deleted)} files")
        
        # Combine parts
        if parts:
            message = " and ".join(parts)
        else:
            message = "Update repository"
        
        # Add file type context if relevant
        if file_types and len(file_types) == 1:
            ext = list(file_types.keys())[0]
            if ext in ['.py', '.js', '.java', '.cpp']:
                message = f"{message} ({ext[1:]} code)"
        
        return message
    
    def _analyze_commit_quality(self, staged_changes: List[Dict]) -> Dict[str, Any]:
        """Analyze the quality of the pending commit."""
        analysis = {
            'files_count': len(staged_changes),
            'change_types': list(set(c['status'] for c in staged_changes)),
            'file_types': list(set(c['extension'] for c in staged_changes if c['extension'])),
            'complexity': 'Low'
        }
        
        # Assess complexity
        if len(staged_changes) > 10:
            analysis['complexity'] = 'High'
        elif len(staged_changes) > 5:
            analysis['complexity'] = 'Medium'
        
        # Quality indicators
        analysis['quality_indicators'] = []
        
        if len(set(c['extension'] for c in staged_changes)) == 1:
            analysis['quality_indicators'].append('Focused on single file type')
        
        if len(staged_changes) <= 5:
            analysis['quality_indicators'].append('Manageable change size')
        
        return analysis
    
    def _assess_repository_state(self, staged: List[Dict], unstaged: List[Dict], untracked: List[str]) -> str:
        """Assess the overall repository state."""
        if len(staged) == 0 and len(unstaged) == 0 and len(untracked) == 0:
            return 'clean'
        elif len(staged) > 0 and len(unstaged) == 0:
            return 'ready_to_commit'
        elif len(unstaged) > 0:
            return 'work_in_progress'
        else:
            return 'mixed_state'
    
    def _assess_operation_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of the Git operation."""
        quality = {
            'operation_success': result.get('success', False),
            'data_completeness': 'data' in result and bool(result['data']),
            'analysis_depth': 'analysis' in result and bool(result['analysis']),
            'insights_provided': 'insights' in result and len(result.get('insights', [])) > 0
        }
        
        # Calculate quality score
        score = sum(quality.values()) / len(quality)
        
        quality['overall_score'] = score
        quality['grade'] = 'Excellent' if score >= 0.9 else 'Good' if score >= 0.7 else 'Fair'
        
        return quality
    
    def _error_response(self, message: str, exception: Exception = None, suggestions: List[str] = None) -> Dict[str, Any]:
        """Generate standardized error response."""
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': suggestions or [
                "Ensure you're in a Git repository directory",
                "Check Git installation and configuration",
                "Initialize repository with: git init",
                "Examples: 'Check git status', 'Show commit history', 'Create feature branch'",
                f"Supported operations: {', '.join(self.git_operations.keys())}",
                "Use specific Git commands for complex operations"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_operations': list(self.git_operations.keys()),
                'supported_operation_types': list(self.operation_types.keys())
            }
        }