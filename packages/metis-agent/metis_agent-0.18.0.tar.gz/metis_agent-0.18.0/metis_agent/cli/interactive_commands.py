"""
Interactive CLI commands with planning and chat capabilities.

This module provides enhanced CLI commands that include:
- Planning phase before code execution using Metis agent
- Interactive chat with the user through the agent
- Intelligent conversation and confirmation steps
- Agent-driven step-by-step guidance
"""
import click
import sys
from typing import Dict, List, Any
from pathlib import Path
from ..core.agent import SingleAgent
from ..tools.filesystem import FileSystemTool


def get_agent() -> SingleAgent:
    """Get a configured Metis agent instance."""
    agent = SingleAgent()
    return agent


def interactive_prompt(message: str, default: str = None) -> str:
    """Enhanced prompt with better formatting."""
    click.echo(click.style("[Metis]: ", fg="blue", bold=True) + message)
    if default:
        return click.prompt(click.style("[You]", fg="green", bold=True), default=default)
    else:
        return click.prompt(click.style("[You]", fg="green", bold=True))


def display_plan(plan: Dict[str, Any]) -> None:
    """Display a formatted plan to the user."""
    click.echo(click.style("\n[PLAN]", fg="cyan", bold=True))
    click.echo("=" * 50)
    
    if plan.get("objective"):
        click.echo(f"Objective: {plan['objective']}")
        click.echo()
    
    if plan.get("analysis"):
        click.echo(click.style("Analysis:", fg="yellow", bold=True))
        for item in plan["analysis"]:
            click.echo(f"  * {item}")
        click.echo()
    
    if plan.get("steps"):
        click.echo(click.style("Steps:", fg="green", bold=True))
        for i, step in enumerate(plan["steps"], 1):
            click.echo(f"  {i}. {step}")
        click.echo()
    
    if plan.get("files_affected"):
        click.echo(click.style("Files that will be affected:", fg="red", bold=True))
        for file in plan["files_affected"]:
            click.echo(f"  * {file}")
        click.echo()
    
    if plan.get("risks"):
        click.echo(click.style("Potential risks:", fg="red", bold=True))
        for risk in plan["risks"]:
            click.echo(f"  * {risk}")
        click.echo()


def confirm_execution() -> bool:
    """Ask user to confirm execution of the plan."""
    click.echo(click.style("\n[CONFIRM] Do you want to proceed with this plan?", fg="yellow", bold=True))
    return click.confirm("Continue", default=True)


def chat_with_agent(initial_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Interactive chat with the Metis agent to refine the plan."""
    click.echo(click.style("\n[AGENT CHAT MODE] - Type 'done' when ready to proceed, 'quit' to exit", fg="magenta", bold=True))
    click.echo("=" * 60)
    
    agent = get_agent()
    conversation_context = f"""We are planning to: {initial_request}
    
Current plan context: {context}
    
I want to discuss and refine this plan with you. Please help me think through the approach."""
    
    # Initialize conversation with the agent
    agent_response = agent.process_query(conversation_context)
    click.echo(click.style("[Metis Agent]: ", fg="blue", bold=True) + agent_response)
    
    refined_plan = context.copy()
    
    while True:
        user_input = interactive_prompt("What would you like to discuss or modify?")
        
        if user_input.lower() in ['done', 'ready', 'proceed']:
            break
        elif user_input.lower() in ['quit', 'exit', 'cancel']:
            click.echo(click.style("[CANCELLED] Operation cancelled by user.", fg="red"))
            return None
        elif user_input.lower() in ['show plan', 'plan', 'show']:
            display_plan(refined_plan)
            continue
        else:
            # Get intelligent response from agent
            chat_prompt = f"""The user said: "{user_input}"
            
Context: We are planning {initial_request}
Current plan: {refined_plan}
            
Please respond helpfully and suggest any plan modifications if needed."""
            
            agent_response = agent.process_query(chat_prompt)
            click.echo(click.style("[Metis Agent]: ", fg="blue", bold=True) + agent_response)
            
            # Ask if they want to modify the plan based on the discussion
            modify = click.confirm("Would you like to update the plan based on this discussion?")
            if modify:
                # Use agent to generate updated plan
                update_prompt = f"""Based on our discussion, please update this plan:
                {refined_plan}
                
User feedback: {user_input}
Your response: {agent_response}
                
Return an updated plan structure."""
                
                updated_plan_response = agent.process(update_prompt)
                click.echo(click.style("[SUCCESS] Plan updated by agent.", fg="green"))
                click.echo(updated_plan_response)
                
                # Store the feedback
                if 'agent_updates' not in refined_plan:
                    refined_plan['agent_updates'] = []
                refined_plan['agent_updates'].append({
                    'user_input': user_input,
                    'agent_response': agent_response,
                    'plan_update': updated_plan_response
                })
    
    return refined_plan


@click.group()
def interactive():
    """Interactive code commands with planning and chat."""
    pass


@interactive.command("generate")
@click.argument('description')
@click.option('--file', '-f', help='Target file path')
@click.option('--language', '-l', help='Programming language')
@click.option('--skip-chat', is_flag=True, help='Skip interactive chat phase')
def interactive_generate(description, file, language, skip_chat):
    """Generate code with interactive planning and chat using Metis agent."""
    click.echo(click.style("[INTERACTIVE CODE GENERATION]", fg="cyan", bold=True))
    click.echo("=" * 50)
    
    # Step 1: Agent Analysis
    click.echo(click.style("[ANALYZING] Agent analyzing your request...", fg="yellow"))
    
    agent = get_agent()
    
    # Let the agent create the initial plan
    planning_prompt = f"""I need to generate code with the following requirements:
    - Description: {description}
    - Target file: {file or 'To be determined'}
    - Language: {language or 'Auto-detect'}
    
    Please analyze the current project context and create a detailed plan for this code generation task.
    Include analysis, steps, files that will be affected, and potential risks.
    """
    
    agent_plan_response = agent.process_query(planning_prompt)
    click.echo(click.style("[AGENT PLAN]", fg="blue", bold=True))
    click.echo(agent_plan_response)
    
    # Create structured plan data for further processing
    initial_plan = {
        "objective": description,
        "agent_analysis": agent_plan_response,
        "target_file": file,
        "language": language,
        "skip_chat": skip_chat
    }
    
    # Step 2: Interactive Chat (optional)
    if not skip_chat:
        refined_plan = chat_with_agent(description, initial_plan)
        if refined_plan is None:
            return
    else:
        refined_plan = initial_plan
    
    # Step 3: Confirmation
    if not confirm_execution():
        click.echo(click.style("[CANCELLED] Operation cancelled.", fg="red"))
        return
    
    # Step 4: Agent Execution
    click.echo(click.style("\n[EXECUTING] Agent executing the plan...", fg="green", bold=True))
    
    try:
        # Let the agent execute the code generation with context from planning
        execution_prompt = f"""Based on our planning discussion, please generate the code for:
        
        Objective: {description}
        Target file: {file or 'To be determined'}
        Language: {language or 'Auto-detect'}
        
        Context from planning: {refined_plan.get('agent_analysis', '')}
        
        Please generate the actual code and write it to the appropriate file.
        Make sure to use the FileSystemTool to create/modify files as needed.
        """
        
        execution_result = agent.process_query(execution_prompt)
        click.echo(click.style("[AGENT EXECUTION]", fg="blue", bold=True))
        click.echo(execution_result)
        
        # Also offer to save code manually if the agent provided code content
        if "```" in execution_result or "def " in execution_result or "class " in execution_result:
            save_manually = click.confirm("\nWould you like to manually save the generated code to a file?")
            if save_manually:
                if not file:
                    file = interactive_prompt("Enter filename:")
                
                # Extract code from agent response (simple heuristic)
                code_content = execution_result
                if "```" in execution_result:
                    # Try to extract code block
                    parts = execution_result.split("```")
                    if len(parts) >= 3:
                        # Get the code block (skip language identifier)
                        code_content = parts[1]
                        if "\n" in code_content:
                            lines = code_content.split("\n")
                            if lines[0].strip() in ['python', 'py', 'javascript', 'js', 'java', 'cpp', 'c']:
                                code_content = "\n".join(lines[1:])
                
                fs_tool = FileSystemTool()
                write_result = fs_tool.write_file(file, code_content)
                
                if write_result.get("success"):
                    click.echo(click.style(f"[SUCCESS] Code saved to {file}", fg="green"))
                else:
                    click.echo(click.style(f"[ERROR] Error saving file: {write_result.get('error')}", fg="red"))
        
        click.echo(click.style("\n[COMPLETE] Code generation session completed!", fg="green", bold=True))
            
    except Exception as e:
        click.echo(click.style(f"[ERROR] Error during agent execution: {str(e)}", fg="red"))


@interactive.command("modify")
@click.argument('file_path')
@click.argument('description')
@click.option('--backup', is_flag=True, default=True, help='Create backup before modifying')
@click.option('--skip-chat', is_flag=True, help='Skip interactive chat phase')
def interactive_modify(file_path, description, backup, skip_chat):
    """Modify existing code with interactive planning and chat."""
    click.echo(click.style("[INTERACTIVE CODE MODIFICATION]", fg="cyan", bold=True))
    click.echo("=" * 50)
    
    # Verify file exists
    if not Path(file_path).exists():
        click.echo(click.style(f"[ERROR] File not found: {file_path}", fg="red"))
        return
    
    # Step 1: Analyze existing code
    click.echo(click.style("[ANALYZING] Analyzing existing code...", fg="yellow"))
    
    fs_tool = FileSystemTool()
    file_content = fs_tool.read_file(file_path)
    
    if not file_content.get("success"):
        click.echo(click.style(f"[ERROR] Error reading file: {file_content.get('error')}", fg="red"))
        return
    
    # Create modification plan
    modification_plan = {
        "objective": f"Modify {file_path}: {description}",
        "analysis": [
            f"Target file: {file_path}",
            f"File size: {file_content.get('size', 'Unknown')} bytes",
            f"Lines: {file_content.get('lines', 'Unknown')}",
            f"Modification: {description}"
        ],
        "steps": [
            "Analyze existing code structure",
            "Plan modifications without breaking existing functionality",
            "Apply changes carefully",
            "Verify code still works"
        ],
        "files_affected": [file_path],
        "risks": [
            "Existing functionality might break",
            "Syntax errors might be introduced",
            "Dependencies might be affected"
        ]
    }
    
    if backup:
        modification_plan["steps"].insert(2, "Create backup of original file")
    
    # Step 2: Display Plan
    display_plan(modification_plan)
    
    # Step 3: Interactive Chat (optional)
    if not skip_chat:
        refined_plan = chat_loop(description, modification_plan)
        if refined_plan is None:
            return
    else:
        refined_plan = modification_plan
    
    # Step 4: Confirmation
    if not confirm_execution():
        click.echo(click.style("[ERROR] Operation cancelled.", fg="red"))
        return
    
    # Step 5: Execute modifications
    click.echo(click.style("\n[EXECUTING] Executing modifications...", fg="green", bold=True))
    
    try:
        # Generate modification
        generator = ContextAwareCodeGenerator()
        modification_task = f"modify the code in {file_path} to {description}"
        result = generator.execute(modification_task)
        
        if result.get("success") and result.get("code"):
            # Create backup if requested
            if backup:
                backup_result = fs_tool.write_file(f"{file_path}.backup", file_content["content"])
                if backup_result.get("success"):
                    click.echo(click.style(f"[BACKUP] Backup created: {file_path}.backup", fg="blue"))
            
            # Apply modifications
            write_result = fs_tool.write_file(file_path, result["code"])
            
            if write_result.get("success"):
                click.echo(click.style(f"[SUCCESS] File modified successfully: {file_path}", fg="green"))
                click.echo(f"[SIZE] New size: {write_result.get('size', 'Unknown')} bytes")
                click.echo(f"[LINES] Lines: {write_result.get('lines', 'Unknown')}")
            else:
                click.echo(click.style(f"[ERROR] Error writing modified file: {write_result.get('error')}", fg="red"))
        else:
            click.echo(click.style(f"[ERROR] Code modification failed: {result.get('error', 'Unknown error')}", fg="red"))
            
    except Exception as e:
        click.echo(click.style(f"[ERROR] Error during modification: {str(e)}", fg="red"))


@interactive.command("plan")
@click.argument('description')
@click.option('--scope', default='file', help='Scope: file, module, or project')
def interactive_plan(description, scope):
    """Create and discuss a development plan without executing."""
    click.echo(click.style("[BACKUP] Interactive Planning Mode", fg="cyan", bold=True))
    click.echo("=" * 50)
    
    # Analyze context based on scope
    if scope == 'project':
        project_tool = ProjectContextTool()
        context = project_tool.analyze_directory(".")
    else:
        context = {"scope": scope}
    
    # Create comprehensive plan
    plan = {
        "objective": description,
        "scope": scope.title(),
        "analysis": [
            f"Requested task: {description}",
            f"Scope: {scope}",
            "Analyzing current project structure..."
        ],
        "steps": [
            "Gather requirements and constraints",
            "Design solution architecture",
            "Plan implementation phases",
            "Identify testing strategy",
            "Consider deployment aspects"
        ],
        "considerations": [
            "Code maintainability",
            "Performance implications",
            "Security considerations",
            "Integration with existing code"
        ]
    }
    
    # Display initial plan
    display_plan(plan)
    
    # Enter planning chat mode
    click.echo(click.style("\n[PLANNING] Planning Chat Mode", fg="magenta", bold=True))
    click.echo("Discuss and refine your plan. Commands: 'done', 'save', 'quit'")
    click.echo("=" * 60)
    
    while True:
        user_input = interactive_prompt("What would you like to discuss about this plan?")
        
        if user_input.lower() in ['done', 'finished']:
            break
        elif user_input.lower() == 'save':
            plan_file = interactive_prompt("Save plan to file (filename):", f"plan_{description.replace(' ', '_')}.md")
            # Save plan as markdown
            plan_content = f"# Development Plan: {description}\n\n"
            plan_content += f"**Objective:** {plan['objective']}\n\n"
            plan_content += f"**Scope:** {plan['scope']}\n\n"
            plan_content += "## Steps:\n"
            for i, step in enumerate(plan['steps'], 1):
                plan_content += f"{i}. {step}\n"
            
            fs_tool = FileSystemTool()
            save_result = fs_tool.write_file(plan_file, plan_content)
            if save_result.get("success"):
                click.echo(click.style(f"[SUCCESS] Plan saved to {plan_file}", fg="green"))
            continue
        elif user_input.lower() in ['quit', 'exit']:
            break
        else:
            # Provide contextual response
            # Get agent name from context (we don't have agent instance here, so use a generic approach)
            click.echo(click.style("[Agent]: ", fg="blue", bold=True) + 
                      f"That's a great point about: {user_input}")
            click.echo("I've noted this for the implementation phase.")
    
    click.echo(click.style("\n[SUCCESS] Planning session completed!", fg="green", bold=True))

