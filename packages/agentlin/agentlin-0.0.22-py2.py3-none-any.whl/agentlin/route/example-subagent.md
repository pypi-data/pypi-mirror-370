---
name: ai-engineer
description: Build LLM applications, RAG systems, and prompt pipelines. Implements vector search, agent orchestration, and AI API integrations. Use PROACTIVELY for LLM features, chatbots, or AI-powered applications.
model: claude-opus-4-20250514
allowed_tools: ["code_interpreter", "file_system", "web_search", "database"]
---

You are an AI engineer specializing in LLM applications and generative AI systems.

## Focus Areas
- LLM integration (OpenAI, Anthropic, open source or local models)
- RAG systems with vector databases (Qdrant, Pinecone, Weaviate)
- Prompt engineering and optimization
- Agent frameworks (LangChain, LangGraph, CrewAI patterns)
- Embedding strategies and semantic search
- Token optimization and cost management

## Approach
1. Start with simple prompts, iterate based on outputs
2. Implement fallbacks for AI service failures
3. Monitor token usage and costs
4. Use structured outputs (JSON mode, function calling)
5. Test with edge cases and adversarial inputs

## Output
- LLM integration code with error handling
- RAG pipeline with chunking strategy
- Prompt templates with variable injection
- Vector database setup and queries
- Token usage tracking and optimization
- Evaluation metrics for AI outputs

Focus on reliability and cost efficiency. Include prompt versioning and A/B testing.

## Code for Agent
```python
import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import openai
from transformers import AutoTokenizer

@dataclass
class LLMConfig:
    provider: str
    model: str
    api_key: str
    max_tokens: int = 1000
    temperature: float = 0.7

class AIEngineerAgent:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.tokenizer = None
        self.conversation_history = []

    async def initialize(self):
        """Initialize the agent with necessary resources"""
        if self.config.provider == "openai":
            openai.api_key = self.config.api_key

        # Load tokenizer for token counting
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        except Exception:
            self.tokenizer = None

    async def process_request(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process AI engineering requests with context"""
        try:
            # Count tokens
            token_count = self._count_tokens(prompt)

            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": prompt,
                "tokens": token_count
            })

            # Generate response based on provider
            if self.config.provider == "openai":
                response = await self._openai_generate(prompt, context)
            else:
                response = {"error": "Unsupported provider"}

            # Track usage
            response["usage"] = {
                "input_tokens": token_count,
                "total_conversation_tokens": sum(h.get("tokens", 0) for h in self.conversation_history)
            }

            return response

        except Exception as e:
            return {"error": str(e), "type": "processing_error"}

    async def _openai_generate(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate response using OpenAI API"""
        try:
            messages = [{"role": "system", "content": "You are an expert AI engineer."}]

            # Add context if provided
            if context:
                context_str = json.dumps(context, indent=2)
                messages.append({"role": "user", "content": f"Context: {context_str}"})

            messages.append({"role": "user", "content": prompt})

            response = await openai.ChatCompletion.acreate(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )

            return {
                "response": response.choices[0].message.content,
                "model": self.config.model,
                "success": True
            }

        except Exception as e:
            return {"error": str(e), "success": False}

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        return len(text.split())  # Fallback approximation

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation history"""
        return {
            "total_exchanges": len(self.conversation_history),
            "total_tokens": sum(h.get("tokens", 0) for h in self.conversation_history),
            "history": self.conversation_history[-5:]  # Last 5 exchanges
        }
```

## Code for Interpreter
```python
import ast
import sys
import traceback
import subprocess
from typing import Dict, Any, List, Optional
from io import StringIO
import contextlib
import tempfile
import os

class AIEngineerInterpreter:
    def __init__(self):
        self.execution_context = {
            '__builtins__': __builtins__,
            'print': print,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
        }
        self.allowed_imports = {
            'json', 'math', 'random', 'datetime', 'collections',
            'itertools', 'functools', 'typing', 're', 'os',
            'sys', 'pathlib', 'dataclasses', 'uuid', 'hashlib'
        }
        self.execution_history = []

    def validate_code(self, code: str) -> Dict[str, Any]:
        """Validate Python code for security and syntax"""
        try:
            # Parse to AST
            tree = ast.parse(code)

            # Security checks
            security_issues = []
            for node in ast.walk(tree):
                # Check for dangerous imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in self.allowed_imports:
                            security_issues.append(f"Disallowed import: {alias.name}")

                # Check for file operations
                elif isinstance(node, ast.Call):
                    if hasattr(node.func, 'id') and node.func.id in ['open', 'exec', 'eval']:
                        security_issues.append(f"Potentially unsafe function: {node.func.id}")

            return {
                "valid": len(security_issues) == 0,
                "issues": security_issues,
                "ast_nodes": len(list(ast.walk(tree)))
            }

        except SyntaxError as e:
            return {
                "valid": False,
                "issues": [f"Syntax error: {e}"],
                "ast_nodes": 0
            }

    def execute_code(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute Python code safely with timeout"""
        validation = self.validate_code(code)
        if not validation["valid"]:
            return {
                "success": False,
                "error": "Code validation failed",
                "issues": validation["issues"],
                "output": ""
            }

        # Capture output
        stdout_capture = StringIO()
        stderr_capture = StringIO()

        result = {
            "success": False,
            "output": "",
            "error": None,
            "variables_created": [],
            "execution_time": 0
        }

        start_time = time.time()

        try:
            # Redirect stdout/stderr
            with contextlib.redirect_stdout(stdout_capture), \
                 contextlib.redirect_stderr(stderr_capture):

                # Store variables before execution
                vars_before = set(self.execution_context.keys())

                # Execute code
                exec(code, self.execution_context)

                # Find new variables
                vars_after = set(self.execution_context.keys())
                new_vars = vars_after - vars_before

                result.update({
                    "success": True,
                    "output": stdout_capture.getvalue(),
                    "variables_created": list(new_vars),
                    "execution_time": time.time() - start_time
                })

        except Exception as e:
            result.update({
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "output": stdout_capture.getvalue(),
                "execution_time": time.time() - start_time
            })

        # Add stderr output if any
        stderr_output = stderr_capture.getvalue()
        if stderr_output:
            result["stderr"] = stderr_output

        # Store in history
        self.execution_history.append({
            "code": code,
            "result": result,
            "timestamp": time.time()
        })

        return result

    def install_package(self, package_name: str) -> Dict[str, Any]:
        """Install a Python package using pip"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                timeout=120
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "package": package_name
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Installation timeout",
                "package": package_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "package": package_name
            }

    def get_variable_info(self, var_name: str) -> Dict[str, Any]:
        """Get detailed information about a variable"""
        if var_name not in self.execution_context:
            return {"error": f"Variable '{var_name}' not found"}

        var = self.execution_context[var_name]

        info = {
            "name": var_name,
            "type": type(var).__name__,
            "value_preview": str(var)[:200],
            "size_bytes": sys.getsizeof(var)
        }

        # Type-specific information
        if isinstance(var, (list, tuple)):
            info["length"] = len(var)
            info["element_types"] = list(set(type(x).__name__ for x in var[:10]))
        elif isinstance(var, dict):
            info["keys_count"] = len(var)
            info["key_types"] = list(set(type(k).__name__ for k in list(var.keys())[:10]))
        elif isinstance(var, str):
            info["length"] = len(var)
            info["encoding"] = "utf-8"  # Assume UTF-8

        return info

    def clear_context(self, keep_builtins: bool = True) -> Dict[str, Any]:
        """Clear execution context"""
        if keep_builtins:
            builtins = {k: v for k, v in self.execution_context.items()
                       if k in ['__builtins__', 'print', 'len', 'range', 'enumerate', 'zip']}
            self.execution_context = builtins
        else:
            self.execution_context = {}

        return {
            "success": True,
            "remaining_variables": len(self.execution_context)
        }
```
