"""
Web server for Metis Agent.

This module provides a Flask-based web server for interacting with the agent.
"""
import os
import json
import uuid
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify, session
from ..core import SingleAgent

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24).hex())

# Global agent instance
_agent_instance = None


def get_agent():
    """Get or create the agent instance."""
    global _agent_instance
    
    if _agent_instance is None:
        use_titans_memory = app.config.get('USE_TITANS_MEMORY', False)
        _agent_instance = SingleAgent(use_titans_memory=use_titans_memory)
        
    return _agent_instance


def get_session_id():
    """Get or create a session ID for the current user."""
    if 'user_id' not in session:
        session['user_id'] = f"user_{uuid.uuid4().hex[:8]}"
        
    return session['user_id']


@app.route('/')
def index():
    """Root endpoint."""
    return jsonify({
        "status": "ok",
        "message": "Metis Agent API is running",
        "version": "0.1.1"
    })


@app.route('/api/query', methods=['POST'])
def process_query():
    """Process a query from the user."""
    try:
        # Get the query from the request
        data = request.json
        query = data.get('query', '')
        
        if not query.strip():
            return jsonify({'error': 'Query cannot be empty'})
            
        # Get the session ID
        session_id = get_session_id()
        
        # Get the agent
        agent = get_agent()
        
        # Process the query
        response = agent.process_query(query, session_id=session_id)
        
        # Return the response
        return jsonify({
            'content': response,
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        })


@app.route('/api/agent-identity', methods=['GET'])
def get_agent_identity():
    """Return the agent identity information."""
    try:
        # Get the agent
        agent = get_agent()
        
        # Get identity information
        identity = agent.get_agent_identity()
        
        return jsonify(identity)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        })


@app.route('/api/memory-insights', methods=['GET'])
def get_memory_insights():
    """Return memory insights."""
    try:
        # Get the agent
        agent = get_agent()
        
        # Get memory insights
        insights = agent.get_memory_insights()
        
        return jsonify(insights)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        })


@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Return available tools."""
    try:
        from ..tools import get_available_tools
        
        tools = get_available_tools()
        
        return jsonify({
            'tools': tools
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        })


if __name__ == '__main__':
    app.run(debug=True)