"""
Git Integration Tool for Metis Agent CLI.

This tool provides comprehensive git operations including status checking,
history analysis, commit message generation, and code review assistance.
"""

import os
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

from .base import BaseTool


class GitIntegrationTool(BaseTool):
    """Tool for Git integration and version control assistance."""
    
    def __init__(self):
        super().__init__()
    
    def can_handle(self, task: str) -> bool:
        """Check if this tool can handle the given task."""
        git_keywords = [
            "git", "commit", "branch", "merge", "pull", "push", "status",
            "history", "diff", "log", "repository", "version control",
            "code review", "changes", "staged", "unstaged"
        ]
        return any(keyword in task.lower() for keyword in git_keywords)
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute git-related operations."""
        try:
            # Get current working directory
            cwd = kwargs.get("cwd", os.getcwd())
            
            # Check if we're in a git repository
            if not self._is_git_repo(cwd):
                return {
                    "success": False,
                    "error": "Not in a git repository. Use 'git init' to initialize one.",
                    "suggestion": "Initialize git repository with: git init"
                }
            
            task_lower = task.lower()
            
            if "status" in task_lower:
                return self._get_git_status(cwd)
            elif "history" in task_lower or "log" in task_lower:
                return self._get_git_history(cwd)
            elif "commit" in task_lower and "message" in task_lower:
                return self._generate_commit_message(cwd)
            elif "diff" in task_lower:
                return self._get_git_diff(cwd)
            elif "branch" in task_lower:
                return self._get_branch_info(cwd)
            elif "review" in task_lower:
                return self._analyze_for_review(cwd)
            elif "create branch" in task_lower or "feature branch" in task_lower:
                return self._create_feature_branch(cwd, task)
            elif "switch branch" in task_lower or "checkout" in task_lower:
                return self._switch_branch(cwd, task)
            elif "list branches" in task_lower:
                return self._list_branches(cwd)
            else:
                return self._get_general_git_info(cwd)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Git operation failed: {str(e)}"
            }
    
    def _is_git_repo(self, cwd: str) -> bool:
        """Check if current directory is a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def _run_git_command(self, cmd: List[str], cwd: str) -> subprocess.CompletedProcess:
        """Run a git command and return the result."""
        return subprocess.run(
            ["git"] + cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
    
    def _get_git_status(self, cwd: str) -> Dict[str, Any]:
        """Get detailed git status with AI insights."""
        try:
            # Get status
            status_result = self._run_git_command(["status", "--porcelain"], cwd)
            if status_result.returncode != 0:
                return {"success": False, "error": status_result.stderr}
            
            # Parse status
            staged_files = []
            unstaged_files = []
            untracked_files = []
            
            for line in status_result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                status_code = line[:2]
                filename = line[3:].strip()
                
                if status_code[0] != ' ' and status_code[0] != '?':
                    staged_files.append({
                        "file": filename,
                        "status": self._interpret_status_code(status_code[0])
                    })
                
                if status_code[1] != ' ':
                    unstaged_files.append({
                        "file": filename,
                        "status": self._interpret_status_code(status_code[1])
                    })
                
                if status_code == '??':
                    untracked_files.append(filename)
            
            # Get current branch
            branch_result = self._run_git_command(["branch", "--show-current"], cwd)
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            # Generate insights
            insights = self._generate_status_insights(staged_files, unstaged_files, untracked_files)
            
            return {
                "success": True,
                "current_branch": current_branch,
                "staged_files": staged_files,
                "unstaged_files": unstaged_files,
                "untracked_files": untracked_files,
                "insights": insights,
                "suggestions": self._get_status_suggestions(staged_files, unstaged_files, untracked_files)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Status check failed: {str(e)}"}
    
    def _interpret_status_code(self, code: str) -> str:
        """Interpret git status codes."""
        status_map = {
            'A': 'Added',
            'M': 'Modified',
            'D': 'Deleted',
            'R': 'Renamed',
            'C': 'Copied',
            'U': 'Unmerged',
            '?': 'Untracked'
        }
        return status_map.get(code, 'Unknown')
    
    def _generate_status_insights(self, staged: List[Dict], unstaged: List[Dict], untracked: List[str]) -> List[str]:
        """Generate AI insights about repository status."""
        insights = []
        
        total_changes = len(staged) + len(unstaged)
        
        if total_changes == 0 and len(untracked) == 0:
            insights.append("+ Repository is clean - no changes to commit")
        elif len(staged) > 0 and len(unstaged) == 0:
            insights.append(f"+ Ready to commit {len(staged)} staged change(s)")
        elif len(unstaged) > 0:
            insights.append(f"- {len(unstaged)} file(s) have unstaged changes")
        
        if len(untracked) > 0:
            insights.append(f"- {len(untracked)} untracked file(s) found")
            
        # Analyze file types
        all_files = [f["file"] for f in staged] + [f["file"] for f in unstaged] + untracked
        file_types = {}
        for file in all_files:
            ext = os.path.splitext(file)[1]
            file_types[ext] = file_types.get(ext, 0) + 1
        
        if file_types:
            most_common = max(file_types, key=file_types.get)
            if most_common:
                insights.append(f"+ Most changes in {most_common} files")
        
        return insights
    
    def _get_status_suggestions(self, staged: List[Dict], unstaged: List[Dict], untracked: List[str]) -> List[str]:
        """Generate suggestions based on current status."""
        suggestions = []
        
        if len(unstaged) > 0:
            suggestions.append("Stage changes with: git add <file> or git add .")
        
        if len(staged) > 0:
            suggestions.append("Commit staged changes with: git commit -m \"message\"")
        
        if len(untracked) > 0:
            suggestions.append("Add untracked files with: git add <file>")
            
        return suggestions
    
    def _get_git_history(self, cwd: str) -> Dict[str, Any]:
        """Get git commit history with analysis."""
        try:
            # Get recent commits
            log_result = self._run_git_command([
                "log", "--oneline", "-10", "--pretty=format:%h|%an|%ar|%s"
            ], cwd)
            
            if log_result.returncode != 0:
                return {"success": False, "error": log_result.stderr}
            
            commits = []
            for line in log_result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })
            
            # Analyze commit patterns
            analysis = self._analyze_commit_patterns(commits)
            
            return {
                "success": True,
                "branch_name": branch_name,
                "message": f"+ Created and switched to feature branch '{branch_name}'",
                "suggestions": [
                    "+ Start making your changes",
                    "+ Use 'metis git status' to track progress",
                    "+ Commit with 'metis git commit' when ready"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Branch creation failed: {str(e)}"}
    
    def _switch_branch(self, cwd: str, task: str) -> Dict[str, Any]:
        """Switch to a different branch."""
        
        # Analyze commit message patterns
        message_words = []
        authors = {}
        
        for commit in commits:
            message = commit["message"].lower()
            words = re.findall(r'\w+', message)
            message_words.extend(words)
            
            author = commit["author"]
            authors[author] = authors.get(author, 0) + 1
        
        # Find common words
        word_freq = {}
        for word in message_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        insights = [
            f"+ {len(commits)} recent commits analyzed",
            f"+ {len(authors)} contributor(s)"
        ]
        
        if common_words:
            top_word = common_words[0][0]
            insights.append(f"+ Most common commit word: '{top_word}'")
        
        return {
            "total": len(commits),
            "authors": len(authors),
            "common_words": common_words,
            "insights": insights
        }
    
    def _generate_commit_message(self, cwd: str) -> Dict[str, Any]:
        """Generate AI-powered commit message based on staged changes."""
        try:
            # Get staged changes
            diff_result = self._run_git_command(["diff", "--cached", "--name-status"], cwd)
            if diff_result.returncode != 0:
                return {"success": False, "error": "No staged changes found"}
            
            changes = []
            for line in diff_result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t', 1)
                    if len(parts) == 2:
                        status, filename = parts
                        changes.append({
                            "status": self._interpret_status_code(status),
                            "file": filename
                        })
            
            if not changes:
                return {"success": False, "error": "No staged changes to commit"}
            
            # Generate commit message
            message = self._create_commit_message(changes)
            
            return {
                "success": True,
                "suggested_message": message,
                "changes_summary": changes,
                "command": f"git commit -m \"{message}\""
            }
            
        except Exception as e:
            return {"success": False, "error": f"Commit message generation failed: {str(e)}"}
    
    def _create_commit_message(self, changes: List[Dict]) -> str:
        """Create a commit message based on changes."""
        if not changes:
            return "Update files"
        
        # Categorize changes
        added_files = [c["file"] for c in changes if c["status"] == "Added"]
        modified_files = [c["file"] for c in changes if c["status"] == "Modified"]
        deleted_files = [c["file"] for c in changes if c["status"] == "Deleted"]
        
        parts = []
        
        if len(added_files) == 1:
            parts.append(f"Add {os.path.basename(added_files[0])}")
        elif len(added_files) > 1:
            parts.append(f"Add {len(added_files)} files")
        
        if len(modified_files) == 1:
            parts.append(f"Update {os.path.basename(modified_files[0])}")
        elif len(modified_files) > 1:
            parts.append(f"Update {len(modified_files)} files")
        
        if len(deleted_files) == 1:
            parts.append(f"Remove {os.path.basename(deleted_files[0])}")
        elif len(deleted_files) > 1:
            parts.append(f"Remove {len(deleted_files)} files")
        
        if parts:
            return " and ".join(parts)
        else:
            return "Update repository"
    
    def _get_git_diff(self, cwd: str) -> Dict[str, Any]:
        """Get git diff with summary."""
        try:
            # Get unstaged diff
            diff_result = self._run_git_command(["diff", "--stat"], cwd)
            if diff_result.returncode != 0:
                return {"success": False, "error": diff_result.stderr}
            
            return {
                "success": True,
                "diff_summary": diff_result.stdout,
                "suggestion": "Use 'git diff <file>' for detailed changes"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Diff retrieval failed: {str(e)}"}
    
    def _get_branch_info(self, cwd: str) -> Dict[str, Any]:
        """Get branch information and analysis."""
        try:
            # Get all branches
            branch_result = self._run_git_command(["branch", "-a"], cwd)
            if branch_result.returncode != 0:
                return {"success": False, "error": branch_result.stderr}
            
            branches = []
            current_branch = ""
            
            for line in branch_result.stdout.strip().split('\n'):
                if line.startswith('*'):
                    current_branch = line[2:].strip()
                    branches.append({"name": current_branch, "current": True})
                else:
                    branch_name = line.strip()
                    if branch_name and not branch_name.startswith('remotes/'):
                        branches.append({"name": branch_name, "current": False})
            
            return {
                "success": True,
                "current_branch": current_branch,
                "branches": branches,
                "total_branches": len(branches)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Branch info retrieval failed: {str(e)}"}
    
    def _analyze_for_review(self, cwd: str) -> Dict[str, Any]:
        """Analyze recent changes for code review."""
        try:
            # Get recent changes
            diff_result = self._run_git_command(["diff", "HEAD~1"], cwd)
            if diff_result.returncode != 0:
                return {"success": False, "error": "No recent changes to review"}
            
            # Analyze the diff
            diff_lines = diff_result.stdout.split('\n')
            added_lines = len([l for l in diff_lines if l.startswith('+')])
            removed_lines = len([l for l in diff_lines if l.startswith('-')])
            
            # Get changed files
            name_status = self._run_git_command(["diff", "--name-status", "HEAD~1"], cwd)
            changed_files = []
            if name_status.returncode == 0:
                for line in name_status.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t', 1)
                        if len(parts) == 2:
                            changed_files.append(parts[1])
            
            review_points = []
            if added_lines > removed_lines * 2:
                review_points.append("- Significant code addition - check for complexity")
            if len(changed_files) > 10:
                review_points.append("- Many files changed - ensure coherent changes")
            
            return {
                "success": True,
                "lines_added": added_lines,
                "lines_removed": removed_lines,
                "files_changed": changed_files,
                "review_points": review_points or ["+ Changes look manageable"]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Code review analysis failed: {str(e)}"}
    
    def _get_general_git_info(self, cwd: str) -> Dict[str, Any]:
        """Get general git repository information."""
        try:
            # Get current branch
            branch_result = self._run_git_command(["branch", "--show-current"], cwd)
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            # Get remote info
            remote_result = self._run_git_command(["remote", "-v"], cwd)
            remotes = remote_result.stdout.strip() if remote_result.returncode == 0 else "No remotes"
            
            return {
                "success": True,
                "current_branch": current_branch,
                "remotes": remotes,
                "available_commands": [
                    "git status - Check repository status",
                    "git log - View commit history", 
                    "git diff - Show changes",
                    "git branch - List branches"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Git info retrieval failed: {str(e)}"}
    
    def _create_feature_branch(self, cwd: str, task: str) -> Dict[str, Any]:
        """Create a feature branch for development work."""
        try:
            # Extract branch name from task or generate one
            import re
            from datetime import datetime
            
            # Try to extract meaningful name from task
            name_match = re.search(r'(?:create|feature)\s+branch\s+([\w-]+)', task.lower())
            if name_match:
                branch_name = name_match.group(1)
            else:
                # Generate branch name based on timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                branch_name = f"feature/agent-work-{timestamp}"
            
            # Check if branch already exists
            check_result = self._run_git_command(["branch", "--list", branch_name], cwd)
            if check_result.stdout.strip():
                return {
                    "success": False,
                    "error": f"Branch '{branch_name}' already exists",
                    "suggestion": f"Use 'git checkout {branch_name}' to switch to it"
                }
            
            # Create and switch to new branch
            create_result = self._run_git_command(["checkout", "-b", branch_name], cwd)
            if create_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to create branch: {create_result.stderr}"
                }
            
            return {
                "success": True,
                "branch_name": branch_name,
                "message": f"+ Created and switched to feature branch '{branch_name}'",
                "suggestions": [
                    "+ Start making your changes",
                    "+ Use 'metis git status' to track progress",
                    "+ Commit with 'metis git commit' when ready"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Branch creation failed: {str(e)}"}
    
    def _switch_branch(self, cwd: str, task: str) -> Dict[str, Any]:
        """Switch to a different branch."""
        try:
            # Extract branch name from task
            import re
            name_match = re.search(r'(?:switch|checkout)\s+(?:branch\s+)?([\w/-]+)', task.lower())
            if not name_match:
                return {
                    "success": False,
                    "error": "Please specify branch name: 'switch branch <name>'"
                }
            
            branch_name = name_match.group(1)
            
            # Check if branch exists
            list_result = self._run_git_command(["branch", "--list", branch_name], cwd)
            if not list_result.stdout.strip():
                return {
                    "success": False,
                    "error": f"Branch '{branch_name}' does not exist",
                    "suggestion": f"Create it with: 'metis git create branch {branch_name}'"
                }
            
            # Switch to branch
            switch_result = self._run_git_command(["checkout", branch_name], cwd)
            if switch_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to switch branch: {switch_result.stderr}"
                }
            
            return {
                "success": True,
                "branch_name": branch_name,
                "message": f"+ Switched to branch '{branch_name}'",
                "suggestions": [
                    "+ Use 'metis git status' to see current state",
                    "+ Continue development work"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Branch switch failed: {str(e)}"}
    
    def _list_branches(self, cwd: str) -> Dict[str, Any]:
        """List all branches with current branch highlighted."""
        try:
            # Get all branches
            branches_result = self._run_git_command(["branch", "-a"], cwd)
            if branches_result.returncode != 0:
                return {"success": False, "error": branches_result.stderr}
            
            branches = []
            current_branch = None
            
            for line in branches_result.stdout.split('\n'):
                line = line.strip()
                if line:
                    if line.startswith('* '):
                        current_branch = line[2:]
                        branches.append({"name": current_branch, "current": True})
                    else:
                        branches.append({"name": line, "current": False})
            
            return {
                "success": True,
                "branches": branches,
                "current_branch": current_branch,
                "total_branches": len(branches)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Branch listing failed: {str(e)}"}
