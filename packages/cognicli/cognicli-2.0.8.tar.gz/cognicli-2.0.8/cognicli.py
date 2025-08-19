#!/usr/bin/env python3
"""
CogniCLI - A premium AI command line interface with Transformers and GGUF support,
with tool use, integrated lm-eval benchmarking, Synapse model support, and a dark purple accent.
"""

import sys
import os
import json
import time
import threading
import argparse
import subprocess
import warnings
import signal
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import queue
import weakref
import requests
import re

warnings.filterwarnings('ignore')

COGNICLI_ACCENT = "#800080"  # Dark purple

REQUIRED_PACKAGES = [
    'torch>=2.0.0',
    'transformers>=4.35.0',
    'huggingface-hub>=0.17.0',
    'rich>=13.0.0',
    'colorama>=0.4.6',
    'requests>=2.31.0',
    'psutil>=5.9.0',
    'pyyaml>=6.0',
    'numpy>=1.24.0',
    'tokenizers>=0.14.0',
    'accelerate>=0.24.0',
    'sentencepiece>=0.1.99',
    'protobuf>=4.24.0',
    'lm-eval>=0.4.0'
]

OPTIONAL_PACKAGES = {
    'bitsandbytes': 'bitsandbytes>=0.41.0',
    'llama_cpp': 'llama-cpp-python>=0.2.0',
}

def install_dependencies():
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package.split('>=')[0].replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def install_optional_dependency(package_key: str) -> bool:
    try:
        if package_key == 'bitsandbytes':
            import bitsandbytes
            return True
        elif package_key == 'llama_cpp':
            from llama_cpp import Llama
            return True
        return False
    except ImportError:
        try:
            package = OPTIONAL_PACKAGES[package_key]
            print(f"Installing optional dependency: {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            return True
        except Exception as e:
            print(f"Failed to install {package}: {e}")
            return False

BNB_AVAILABLE = False
GGUF_AVAILABLE = False

def check_optional_imports():
    global BNB_AVAILABLE, GGUF_AVAILABLE
    try:
        import bitsandbytes as bnb
        BNB_AVAILABLE = True
    except ImportError:
        BNB_AVAILABLE = False
    try:
        from llama_cpp import Llama
        GGUF_AVAILABLE = True
    except ImportError:
        GGUF_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.live import Live
    from rich import box
    from rich.align import Align
    from rich.layout import Layout
    from rich.prompt import Prompt, Confirm
    from rich.status import Status
    from rich.traceback import install as install_traceback
    import torch
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
    from huggingface_hub import HfApi, list_models, model_info, hf_hub_download
    import requests
    import psutil
    import yaml
    import numpy as np
    from colorama import init, Fore, Style
    check_optional_imports()
except ImportError:
    install_dependencies()
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.live import Live
    from rich import box
    from rich.align import Align
    from rich.layout import Layout
    from rich.prompt import Prompt, Confirm
    from rich.status import Status
    from rich.traceback import install as install_traceback
    import torch
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
    from huggingface_hub import HfApi, list_models, model_info, hf_hub_download
    import requests
    import psutil
    import yaml
    import numpy as np
    from colorama import init, Fore, Style
    check_optional_imports()

# Install rich traceback handler for better error display
install_traceback()

init()
console = Console()

LOGO = """
█████╗  ██████╗  ██████╗  ███╗   ██╗██╗ ██████╗██╗     ██╗
██╔══  ╗██╔═══██╗██╔════╝ ████╗  ██║██║██╔════╝██║     ██║
██║    ║██║   ██║██║  ███╗██╔██╗ ██║██║██║     ██║     ██║
██║    ║██║   ██║██║   ██║██║╚██╗██║██║██║     ██║     ██║
╚█████╔╝╚██████╔╝╚██████╔╝██║ ╚████║██║╚██████╗███████╗██║
 ╚════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝╚══════╝╚═╝
"""

@dataclass
class ModelConfig:
    name: str
    model_type: str
    precision: str
    context_length: int
    temperature: float
    top_p: float
    max_tokens: int
    device: str = "auto"
    trust_remote_code: bool = True
    use_fast_tokenizer: bool = True
    load_in_8bit: bool = False
    load_in_4bit: bool = False
    torch_dtype: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None

class ModelManager:
    """Enhanced model management with proper state tracking and error recovery"""
    
    def __init__(self, console: Console):
        self.console = console
        self.models: Dict[str, ModelConfig] = {}
        self.current_model_id: Optional[str] = None
        self.current_model: Optional[Any] = None
        self.current_tokenizer: Optional[Any] = None
        self.model_lock = threading.Lock()
        self.api = HfApi()
        self.cache_dir = Path.home() / '.cognicli'
        self.cache_dir.mkdir(exist_ok=True)
        
    def get_current_config(self) -> Optional[ModelConfig]:
        """Get the current model configuration safely"""
        if self.current_model_id and self.current_model_id in self.models:
            return self.models[self.current_model_id]
        return None
    
    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded and ready"""
        return (self.current_model is not None and 
                self.current_tokenizer is not None and 
                self.current_model_id is not None)
    
    def unload_current_model(self):
        """Safely unload the current model and free memory"""
        with self.model_lock:
            if self.current_model is not None:
                # Clear CUDA cache if using GPU
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                # Delete model references
                del self.current_model
                self.current_model = None
                
            if self.current_tokenizer is not None:
                del self.current_tokenizer
                self.current_tokenizer = None
                
            self.current_model_id = None
            self.console.print("[yellow]Model unloaded and memory freed.[/yellow]")
    
    def load_model(self, model_id: str, **kwargs) -> bool:
        """Load a model with enhanced error handling and recovery"""
        try:
            with self.model_lock:
                # Unload current model first
                if self.is_model_loaded():
                    self.unload_current_model()
                
                # Create new config
                config = ModelConfig(
                    name=model_id,
                    model_type=kwargs.get('model_type', 'auto'),
                    precision=kwargs.get('precision', 'auto'),
                    context_length=kwargs.get('context_length', 2048),
                    temperature=kwargs.get('temperature', 0.7),
                    top_p=kwargs.get('top_p', 0.95),
                    max_tokens=kwargs.get('max_tokens', 512),
                    **{k: v for k, v in kwargs.items() if k not in ['model_type', 'precision', 'context_length', 'temperature', 'top_p', 'max_tokens']}
                )
                
                # Load the model based on type
                if config.model_type == "gguf" or kwargs.get('gguf_file'):
                    success = self._load_gguf_model(model_id, config, kwargs.get('gguf_file'))
                else:
                    success = self._load_transformers_model(model_id, config)
                
                if success:
                    self.models[model_id] = config
                    self.current_model_id = model_id
                    config.last_used = datetime.now()
                    return True
                else:
                    return False
                    
        except Exception as e:
            self.console.print(f"[red]Failed to load model: {e}[/red]")
            # Clean up on failure
            self.unload_current_model()
            return False
    
    def _load_gguf_model(self, model_id: str, config: ModelConfig, gguf_file: Optional[str] = None) -> bool:
        """Load a GGUF model with enhanced error handling"""
        try:
            if not GGUF_AVAILABLE:
                self.console.print("[red]GGUF support not available. Install llama-cpp-python.[/red]")
                return False
            
            from llama_cpp import Llama
            
            # Determine GGUF file path
            if gguf_file:
                gguf_path = Path(gguf_file)
                if not gguf_path.exists():
                    self.console.print(f"[red]GGUF file not found: {gguf_file}[/red]")
                    return False
            else:
                gguf_path = self._download_gguf_file(model_id)
                if not gguf_path:
                    return False
            
            # Load model with proper error handling
            try:
                self.current_model = Llama(
                    model_path=str(gguf_path),
                    n_ctx=config.context_length,
                    n_gpu_layers=-1 if torch.cuda.is_available() else 0,
                    verbose=False
                )
                config.model_type = "gguf"
                self.current_tokenizer = None  # GGUF models don't have separate tokenizers
                
                self.console.print(f"[bold green]✅ Loaded GGUF model:[/] {model_id}")
                self.console.print(f"[dim]File: {gguf_path.name}[/dim]")
                return True
                
            except Exception as e:
                self.console.print(f"[red]Failed to load GGUF model: {e}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]GGUF loading error: {e}[/red]")
            return False
    
    def _load_transformers_model(self, model_id: str, config: ModelConfig) -> bool:
        """Load a Transformers model with enhanced error handling"""
        try:
            # Check if this is a Synapse model
            is_synapse = self._is_synapse_model(model_id)
            if is_synapse:
                self.console.print(f"[{COGNICLI_ACCENT}]🧠 Detected Synapse model - loading with custom architecture[/]")
                config.model_type = "synapse"
            else:
                config.model_type = "transformers"
            
            # Get quantization config
            quant_config = self._get_quantization_config(config.precision)
            
            # Load tokenizer first
            try:
                self.current_tokenizer = AutoTokenizer.from_pretrained(
                    model_id,
                    use_fast=config.use_fast_tokenizer,
                    trust_remote_code=config.trust_remote_code
                )
                
                # Handle missing pad token
                if self.current_tokenizer.pad_token is None:
                    self.current_tokenizer.pad_token = self.current_tokenizer.eos_token
                
                # Add special tokens for Synapse models
                if is_synapse:
                    special_tokens = ['<think>', '</think>', '<answer>', '</answer>']
                    self.current_tokenizer.add_special_tokens({'additional_special_tokens': special_tokens})
                
            except Exception as e:
                self.console.print(f"[red]Failed to load tokenizer: {e}[/red]")
                return False
            
            # Load model
            try:
                self.current_model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    device_map=config.device,
                    trust_remote_code=config.trust_remote_code,
                    **quant_config
                )
                
                # Resize embeddings if needed (for Synapse models)
                if is_synapse and hasattr(self.current_model, 'resize_token_embeddings'):
                    self.current_model.resize_token_embeddings(len(self.current_tokenizer))
                
                # Move to GPU if available and not using device_map="auto"
                if config.device == "auto" and torch.cuda.is_available():
                    self.current_model = self.current_model.cuda()
                
                self.console.print(f"[bold green]✅ Loaded {config.model_type.title()} model:[/] {model_id}")
                if torch.cuda.is_available():
                    self.console.print(f"[dim]Device: {self.current_model.device}[/dim]")
                return True
                
            except Exception as e:
                self.console.print(f"[red]Failed to load model: {e}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]Transformers loading error: {e}[/red]")
            return False
    
    def _download_gguf_file(self, model_id: str) -> Optional[Path]:
        """Download GGUF file with progress indication"""
        try:
            files = self.api.list_files(model_id)
            gguf_file = next((f for f in files if f.rfilename.endswith(".gguf")), None)
            
            if not gguf_file:
                self.console.print(f"[red]No GGUF file found for {model_id}[/red]")
                return None
            
            path = self.cache_dir / gguf_file.rfilename
            
            if not path.exists():
                self.console.print(f"[yellow]Downloading GGUF file: {gguf_file.rfilename} ...[/yellow]")
                try:
                    hf_hub_download(
                        repo_id=model_id, 
                        filename=gguf_file.rfilename, 
                        local_dir=self.cache_dir
                    )
                except Exception as e:
                    self.console.print(f"[red]Download failed: {e}[/red]")
                    return None
            
            return path
            
        except Exception as e:
            self.console.print(f"[red]Failed to find GGUF file: {e}[/red]")
            return None
    
    def _is_synapse_model(self, model_id: str) -> bool:
        """Check if a model is a Synapse model by examining its config"""
        try:
            config_info = self.api.model_info(model_id)
            for file_info in config_info.siblings:
                if file_info.rfilename == "config.json":
                    config_path = hf_hub_download(repo_id=model_id, filename="config.json")
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    architectures = config.get("architectures", [])
                    model_type = config.get("model_type", "")
                    auto_map = config.get("auto_map", {})
                    
                    synapse_indicators = [
                        "SynapseMultiMoEModel" in architectures,
                        model_type == "synapse",
                        "synapse" in str(auto_map).lower(),
                        "num_experts" in config,
                        any("synapse" in arch.lower() for arch in architectures)
                    ]
                    
                    return any(synapse_indicators)
        except Exception:
            pass
        return False
    
    def _get_quantization_config(self, precision: str) -> Dict[str, Any]:
        """Get quantization configuration with proper error handling"""
        config = {}
        
        if precision in ("q4", "q8") and BNB_AVAILABLE:
            if precision == "q8":
                config["load_in_8bit"] = True
            elif precision == "q4":
                config["load_in_4bit"] = True
                config["bnb_4bit_compute_dtype"] = torch.float16
                config["bnb_4bit_use_double_quant"] = True
                config["bnb_4bit_quant_type"] = "nf4"
        elif precision in ("fp16", "bf16"):
            dtype_map = {"fp16": torch.float16, "bf16": torch.bfloat16}
            config["torch_dtype"] = dtype_map[precision]
        
        return config

class EnhancedAnimatedSpinner:
    """Enhanced spinner with better terminal handling and no text overlap"""
    
    def __init__(self, text: str, console: Console):
        self.text = text
        self.console = console
        self.spinning = False
        self.thread = None
        self.spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.current_char = 0
        
    def start(self):
        """Start the spinner with proper console handling"""
        if self.spinning:
            return
            
        self.spinning = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the spinner and clean up"""
        self.spinning = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.1)
        
        # Clear the spinner line
        self.console.print("", end="")
    
    def _spin(self):
        """Internal spinning logic with proper console updates"""
        while self.spinning:
            try:
                char = self.spinner_chars[self.current_char % len(self.spinner_chars)]
                spinner_text = f"{char} {self.text}"
                
                # Use rich console for consistent formatting
                self.console.print(f"[{COGNICLI_ACCENT}]{spinner_text}[/{COGNICLI_ACCENT}]", end="\r")
                
                self.current_char += 1
                time.sleep(0.1)
            except Exception:
                break

class ResponseGenerator:
    """Enhanced response generation with proper streaming and error handling"""
    
    def __init__(self, model_manager: ModelManager, console: Console):
        self.model_manager = model_manager
        self.console = console
        self.system_tool_prompt = self._get_system_tool_prompt()
        self.synapse_system_prompt = self._get_synapse_system_prompt()
    
    def _get_system_tool_prompt(self) -> str:
        return """You are CogniCLI, a helpful AI assistant and code agent with tool use.

Available tools:
- write_file(filepath, content): Write the given content to the file at 'filepath'.
- append_file(filepath, content): Append the content to a file.
- read_file(filepath): Read and return content of the file.
- list_dir(path="."): List files in a directory.
- run_shell(cmd): Run the shell command and return output.
- python_eval(code): Run Python code and return output.
- pip_install(package): Pip install a package by name.

If you want to use a tool, respond ONLY with a JSON object of this form:
{"tool_call": "<tool_name>", "args": {"arg1": "value1", ...}}
Otherwise, reply as normal.

Examples:
{"tool_call": "write_file", "args": {"filepath": "main.py", "content": "print('hi')"}}
{"tool_call": "append_file", "args": {"filepath": "main.py", "content": "print('hi again')"}}
{"tool_call": "read_file", "args": {"filepath": "main.py"}}
{"tool_call": "list_dir", "args": {"path": "."}}
{"tool_call": "run_shell", "args": {"cmd": "ls -la"}}
{"tool_call": "python_eval", "args": {"code": "print(1+1)"}}
{"tool_call": "pip_install", "args": {"package": "requests"}}"""

    def _get_synapse_system_prompt(self) -> str:
        return """You are Synapse, a helpful AI assistant with advanced reasoning capabilities. You use a think-answer structure when appropriate.

When solving complex problems:
1. Use <think> tags to show your step-by-step reasoning
2. Use <answer> tags to provide your final response

Available tools:
- write_file(filepath, content): Write content to a file
- append_file(filepath, content): Append content to a file
- read_file(filepath): Read file content
- list_dir(path="."): List directory contents
- run_shell(cmd): Execute shell commands
- python_eval(code): Execute Python code
- pip_install(package): Install Python packages

To use tools, respond with JSON: {"tool_call": "<tool_name>", "args": {"arg1": "value1", ...}}

Examples:
{"tool_call": "write_file", "args": {"filepath": "test.py", "content": "print('Hello')"}}
{"tool_call": "python_eval", "args": {"code": "print(2 + 2)"}}"""

    def generate_response(self, prompt: str, stream: bool = True, show_thinking: bool = True) -> str:
        """Generate response with enhanced error handling and proper formatting"""
        if not self.model_manager.is_model_loaded():
            self.console.print(f"[{COGNICLI_ACCENT}]No model loaded. Use --model to load a model.[/{COGNICLI_ACCENT}]")
            return ""

        config = self.model_manager.get_current_config()
        if not config:
            self.console.print("[red]Model configuration not found.[/red]")
            return ""

        try:
            # Handle different model types
            if config.model_type == "gguf":
                response = self._generate_gguf(prompt, config)
            elif config.model_type == "synapse":
                response = self._generate_synapse(prompt, config)
            else:
                response = self._generate_transformers(prompt, config)

            # Handle tool calls
            tool_call = self._extract_tool_call(response)
            if tool_call:
                self._process_tool_call(tool_call)
            else:
                # Display response with proper formatting
                if config.model_type == "synapse" and show_thinking:
                    self._display_synapse_response(response)
                else:
                    self._display_response(response)

            return response

        except Exception as e:
            self.console.print(f"[red]Generation error: {e}[/red]")
            return ""

    def _generate_gguf(self, prompt: str, config: ModelConfig) -> str:
        """Generate response for GGUF models"""
        try:
            full_prompt = self.system_tool_prompt + "\n\nUser: " + prompt + "\nAssistant:"
            response = self.model_manager.current_model(
                prompt=full_prompt, 
                max_tokens=config.max_tokens, 
                temperature=config.temperature,
                top_p=config.top_p,
                stop=["User:", "\n\n"]
            )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            self.console.print(f"[red]GGUF generation error: {e}[/red]")
            return ""

    def _generate_synapse(self, prompt: str, config: ModelConfig) -> str:
        """Generate response for Synapse models with proper formatting"""
        try:
            system_prompt = self.synapse_system_prompt
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"

            inputs = self.model_manager.current_tokenizer(full_prompt, return_tensors="pt")
            input_ids = inputs["input_ids"].to(self.model_manager.current_model.device)
            attention_mask = inputs.get("attention_mask", None)

            gen_args = {
                "input_ids": input_ids,
                "max_new_tokens": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "do_sample": True,
                "eos_token_id": self.model_manager.current_tokenizer.eos_token_id,
                "pad_token_id": self.model_manager.current_tokenizer.eos_token_id,
                "repetition_penalty": 1.1,
            }

            if attention_mask is not None:
                gen_args["attention_mask"] = attention_mask.to(self.model_manager.current_model.device)

            with torch.no_grad():
                outputs = self.model_manager.current_model.generate(**gen_args)

            response = self.model_manager.current_tokenizer.decode(
                outputs[0][input_ids.shape[1]:],
                skip_special_tokens=True
            )

            return response.strip()

        except Exception as e:
            self.console.print(f"[red]Synapse generation error: {e}[/red]")
            return ""

    def _generate_transformers(self, prompt: str, config: ModelConfig) -> str:
        """Generate response for Transformers models"""
        try:
            full_prompt = self.system_tool_prompt + "\n\nUser: " + prompt + "\nAssistant:"
            
            inputs = self.model_manager.current_tokenizer(full_prompt, return_tensors="pt")
            input_ids = inputs["input_ids"].to(self.model_manager.current_model.device)
            attention_mask = inputs.get("attention_mask", None)
            
            gen_args = {
                "input_ids": input_ids,
                "max_new_tokens": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "do_sample": True,
                "eos_token_id": self.model_manager.current_tokenizer.eos_token_id,
                "pad_token_id": self.model_manager.current_tokenizer.eos_token_id,
            }
            
            if attention_mask is not None:
                gen_args["attention_mask"] = attention_mask.to(self.model_manager.current_model.device)
            
            with torch.no_grad():
                outputs = self.model_manager.current_model.generate(**gen_args)
            
            response = self.model_manager.current_tokenizer.decode(
                outputs[0][input_ids.shape[1]:], 
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            self.console.print(f"[red]Transformers generation error: {e}[/red]")
            return ""

    def _extract_tool_call(self, response: str) -> Optional[Dict]:
        """Extract tool calls from response with improved regex"""
        import re
        
        # Try to find JSON tool calls
        json_pattern = r'\{[^{}]*"tool_call"\s*:\s*"[^"]+"[^{}]*\}'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        for match in matches:
            try:
                obj = json.loads(match)
                if "tool_call" in obj and "args" in obj:
                    return obj
            except json.JSONDecodeError:
                continue
        
        # Try parsing the entire response as JSON
        try:
            obj = json.loads(response.strip())
            if "tool_call" in obj and "args" in obj:
                return obj
        except json.JSONDecodeError:
            pass
        
        return None

    def _process_tool_call(self, tool_call: Dict):
        """Process tool calls with enhanced error handling"""
        tool_name = tool_call.get("tool_call", "")
        args = tool_call.get("args", {})
        
        if tool_name in TOOLS:
            try:
                result = TOOLS[tool_name](**args)
                self.console.print(Panel(
                    result, 
                    title=f"🔧 Tool: {tool_name}", 
                    border_style=COGNICLI_ACCENT
                ))
            except Exception as e:
                self.console.print(Panel(
                    f"❌ Error running tool '{tool_name}': {e}", 
                    title=f"🔧 Tool Error: {tool_name}", 
                    border_style="red"
                ))
        else:
            self.console.print(Panel(
                f"❌ Unknown tool '{tool_name}'", 
                title="🔧 Tool Error", 
                border_style="red"
            ))

    def _display_response(self, response: str):
        """Display response with proper formatting"""
        if not response.strip():
            self.console.print("[dim]No response generated.[/dim]")
            return
        
        try:
            # Try to render as markdown first
            self.console.print(Markdown(response))
        except Exception:
            # Fall back to plain text if markdown fails
            self.console.print(response)

    def _display_synapse_response(self, response: str):
        """Display Synapse model response with proper formatting for thinking tags"""
        import re

        # Extract thinking and answer sections
        think_pattern = r'<think>(.*?)</think>'
        answer_pattern = r'<answer>(.*?)</answer>'

        think_matches = re.findall(think_pattern, response, re.DOTALL)
        answer_matches = re.findall(answer_pattern, response, re.DOTALL)

        # Display thinking section if present
        if think_matches:
            thinking_content = think_matches[0].strip()
            if thinking_content:
                thinking_panel = Panel(
                    thinking_content,
                    title="🤔 Reasoning",
                    border_style="dim",
                    title_style="dim italic"
                )
                self.console.print(thinking_panel)

        # Display answer section if present
        if answer_matches:
            answer_content = answer_matches[0].strip()
            if answer_content:
                self.console.print(Markdown(answer_content))
        else:
            # If no structured format, just display the whole response
            # but remove any remaining think tags
            cleaned_response = re.sub(r'</?(?:think|answer)>', '', response).strip()
            if cleaned_response:
                self.console.print(Markdown(cleaned_response))

def write_file(filepath: str, content: str) -> str:
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Wrote to {filepath}"
    except Exception as e:
        return f"❌ Error writing file: {e}"

def read_file(filepath: str) -> str:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"❌ Error reading file: {e}"

def run_shell(cmd: str) -> str:
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        return f"$ {cmd}\n{result.stdout}{result.stderr}"
    except Exception as e:
        return f"❌ Error running shell command: {e}"

def list_dir(path: str = ".") -> str:
    try:
        files = os.listdir(path)
        return f"Files in {os.path.abspath(path)}:\n" + "\n".join(files)
    except Exception as e:
        return f"❌ Error listing directory: {e}"

def append_file(filepath: str, content: str) -> str:
    try:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Appended to {filepath}"
    except Exception as e:
        return f"❌ Error appending file: {e}"

def python_eval(code: str) -> str:
    import io
    import contextlib
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(code, {}, {})
        return f"Python output:\n{buf.getvalue()}"
    except Exception as e:
        return f"❌ Python error: {e}"

def pip_install(package: str) -> str:
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        return f"✅ Installed package {package}"
    except Exception as e:
        return f"❌ Pip install error: {e}"

TOOLS = {
    "write_file": write_file,
    "read_file": read_file,
    "run_shell": run_shell,
    "list_dir": list_dir,
    "append_file": append_file,
    "python_eval": python_eval,
    "pip_install": pip_install,
}

SYSTEM_TOOL_PROMPT = """
You are CogniCLI, a helpful AI assistant and code agent with tool use.

Available tools:
- write_file(filepath, content): Write the given content to the file at 'filepath'.
- append_file(filepath, content): Append the content to a file.
- read_file(filepath): Read and return content of the file.
- list_dir(path="."): List files in a directory.
- run_shell(cmd): Run the shell command and return output.
- python_eval(code): Run Python code and return output.
- pip_install(package): Pip install a package by name.

If you want to use a tool, respond ONLY with a JSON object of this form:
{"tool_call": "<tool_name>", "args": {"arg1": "value1", ...}}
Otherwise, reply as normal.

Examples:
{"tool_call": "write_file", "args": {"filepath": "main.py", "content": "print('hi')"}}
{"tool_call": "append_file", "args": {"filepath": "main.py", "content": "print('hi again')"}}
{"tool_call": "read_file", "args": {"filepath": "main.py"}}
{"tool_call": "list_dir", "args": {"path": "."}}
{"tool_call": "run_shell", "args": {"cmd": "ls -la"}}
{"tool_call": "python_eval", "args": {"code": "print(1+1)"}}
{"tool_call": "pip_install", "args": {"package": "requests"}}
"""

import re
def extract_tool_call(response: str) -> Optional[Dict]:
    matches = list(re.finditer(r'\{.*"tool_call"\s*:\s*".+?".*\}', response, re.DOTALL))
    for match in matches:
        s = match.group(0)
        try:
            obj = json.loads(s)
            if "tool_call" in obj and "args" in obj:
                return obj
        except Exception:
            continue
    try:
        obj = json.loads(response)
        if "tool_call" in obj and "args" in obj:
            return obj
    except Exception:
        pass
    return None

def process_tool_call(obj: Dict, cli_console=None):
    tool_name = obj["tool_call"]
    args = obj.get("args", {})
    tool_fn = TOOLS.get(tool_name)
    if tool_fn:
        try:
            result = tool_fn(**args)
            if cli_console:
                cli_console.print(Panel(result, title=f"Tool: {tool_name}", border_style=COGNICLI_ACCENT))
            else:
                print(result)
        except Exception as e:
            msg = f"❌ Error running tool '{tool_name}': {e}"
            if cli_console:
                cli_console.print(Panel(msg, title=f"Tool: {tool_name}", border_style=COGNICLI_ACCENT))
            else:
                print(msg)
    else:
        msg = f"❌ Unknown tool '{tool_name}'."
        if cli_console:
            cli_console.print(Panel(msg, title="Tool Error", border_style=COGNICLI_ACCENT))
        else:
            print(msg)


ALL_BENCHMARK_TASKS = [
    "hellaswag", "arc_easy", "arc_challenge", "winogrande", "mmlu",
    "gsm8k", "wikitext", "openbookqa", "piqa", "lambada", "mathqa", "boolq"
]
BENCHMARK_PRESETS = {
    "reasoning": ["hellaswag", "arc_easy", "arc_challenge", "winogrande", "piqa", "gsm8k", "mmlu"],
    "math": ["gsm8k", "mathqa"],
    "reading": ["wikitext", "lambada", "boolq"],
    "all": ALL_BENCHMARK_TASKS
}

class CogniCLI:
    """Enhanced CogniCLI with premium features and robust error handling"""
    
    def __init__(self):
        self.console = Console()
        self.model_manager = ModelManager(self.console)
        self.response_generator = ResponseGenerator(self.model_manager, self.console)
        self.ollama_manager = OllamaManager(self.console)
        self.api = HfApi()
        self.cache_dir = Path.home() / '.cognicli'
        self.cache_dir.mkdir(exist_ok=True)
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.console.print(f"\n[yellow]Received signal {signum}, shutting down gracefully...[/yellow]")
        if self.model_manager.is_model_loaded():
            self.model_manager.unload_current_model()
        sys.exit(0)

    def show_logo(self):
        """Display the enhanced logo with better formatting"""
        logo_text = Text(LOGO)
        logo_text.stylize(f"bold {COGNICLI_ACCENT}")
        
        # Add version and status info
        version_text = Text("v2.0.8 - Premium Edition", style="dim")
        status_text = Text("🚀 Enhanced • Robust • Premium", style="green")
        
        panel = Panel(
            Align.center(logo_text),
            title="CogniCLI",
            subtitle="Premium AI Command Line Interface",
            border_style=COGNICLI_ACCENT,
            padding=(1, 4),
        )
        
        self.console.print(Align.center(panel))
        self.console.print(Align.center(version_text))
        self.console.print(Align.center(status_text))
        self.console.print()

    def list_models(self, filter_term: str = "") -> List[dict]:
        """List models with enhanced filtering and display"""
        try:
            with self.console.status(f"[{COGNICLI_ACCENT}]Searching models...[/{COGNICLI_ACCENT}]"):
                models = self.api.list_models(filter="text-generation")
            
            out = []
            for model in models:
                if filter_term.lower() in model.modelId.lower():
                    info = {
                        "id": model.modelId,
                        "downloads": getattr(model, "downloads", 0),
                        "likes": getattr(model, "likes", 0),
                        "tags": getattr(model, "tags", []),
                        "last_modified": getattr(model, "lastModified", None),
                    }
                    out.append(info)
            
            return sorted(out, key=lambda x: x['downloads'], reverse=True)
            
        except Exception as e:
            self.console.print(f"[red]Failed to list models: {e}[/red]")
            return []

    def show_model_info(self, model_id: str):
        """Show detailed model information with enhanced display"""
        try:
            with self.console.status(f"[{COGNICLI_ACCENT}]Fetching model info...[/{COGNICLI_ACCENT}]"):
                info = self.api.model_info(model_id)
            
            # Create a comprehensive info panel
            info_content = f"""
[bold]{info.modelId}[/bold]

[dim]📊 Statistics:[/dim]
• [green]Downloads:[/green] {info.downloads:,}
• [yellow]Likes:[/yellow] {info.likes:,}
• [blue]Tags:[/blue] {', '.join(info.tags[:10])}{'...' if len(info.tags) > 10 else ''}

[dim]📝 Description:[/dim]
{info.cardData.get('summary', 'No summary available.')}

[dim]🔧 Model Details:[/dim]
• [cyan]Author:[/cyan] {info.author or 'Unknown'}
• [cyan]Pipeline:[/cyan] {', '.join(info.pipeline_tag) if hasattr(info, 'pipeline_tag') else 'Unknown'}
• [cyan]License:[/cyan] {info.license or 'Unknown'}
"""
            
            panel = Panel(
                info_content,
                title=f"Model Information: {model_id}",
                border_style=COGNICLI_ACCENT,
                padding=(1, 2),
            )
            self.console.print(panel)
            
        except Exception as e:
            self.console.print(f"[red]Failed to get info for model: {e}[/red]")

    def show_model_files(self, model_id: str):
        """Show model files with enhanced display and GGUF detection"""
        try:
            with self.console.status(f"[{COGNICLI_ACCENT}]Fetching model files...[/{COGNICLI_ACCENT}]"):
                files = self.api.list_files(model_id)
            
            # Separate GGUF files from others
            gguf_files = [f for f in files if f.rfilename.endswith(".gguf")]
            other_files = [f for f in files if not f.rfilename.endswith(".gguf")]
            
            # Create tables
            if gguf_files:
                gguf_table = Table(
                    title=f"🦙 GGUF Files for {model_id}", 
                    box=box.ROUNDED, 
                    title_style=COGNICLI_ACCENT
                )
                gguf_table.add_column("File Name", style=COGNICLI_ACCENT)
                gguf_table.add_column("Size", style="green")
                gguf_table.add_column("SHA256", style="yellow")
                gguf_table.add_column("Type", style="cyan")
                
                for f in gguf_files:
                    # Determine quantization type from filename
                    q_type = "Unknown"
                    if "q4" in f.rfilename.lower():
                        q_type = "4-bit"
                    elif "q8" in f.rfilename.lower():
                        q_type = "8-bit"
                    elif "q5" in f.rfilename.lower():
                        q_type = "5-bit"
                    
                    gguf_table.add_row(f.rfilename, self._format_size(f.size), f.sha256[:8], q_type)
                
                self.console.print(gguf_table)
                self.console.print()
            
            if other_files:
                other_table = Table(
                    title=f"📁 Other Files for {model_id}", 
                    box=box.ROUNDED, 
                    title_style=COGNICLI_ACCENT
                )
                other_table.add_column("File Name", style=COGNICLI_ACCENT)
                other_table.add_column("Size", style="green")
                other_table.add_column("SHA256", style="yellow")
                
                for f in other_files:
                    other_table.add_row(f.rfilename, self._format_size(f.size), f.sha256[:8])
                
                self.console.print(other_table)
                
        except Exception as e:
            self.console.print(f"[red]Failed to get files for model: {e}[/red]")

    def search_models(self, query: str, limit: int = 20) -> List[dict]:
        """Search for models on Hugging Face with enhanced filtering and display"""
        try:
            with self.console.status(f"[{COGNICLI_ACCENT}]Searching for '{query}'...[/{COGNICLI_ACCENT}]"):
                # Search for models with the query
                models = self.api.list_models(
                    filter="text-generation",
                    search=query,
                    limit=limit * 2  # Get more to filter better
                )
            
            out = []
            for model in models:
                # Enhanced filtering based on query
                query_terms = query.lower().split()
                model_id_lower = model.modelId.lower()
                
                # Check if all query terms are present in model ID
                if all(term in model_id_lower for term in query_terms):
                    info = {
                        "id": model.modelId,
                        "downloads": getattr(model, "downloads", 0),
                        "likes": getattr(model, "likes", 0),
                        "tags": getattr(model, "tags", []),
                        "last_modified": getattr(model, "lastModified", None),
                        "author": getattr(model, "author", "Unknown"),
                        "pipeline_tag": getattr(model, "pipeline_tag", []),
                        "card_data": getattr(model, "cardData", {})
                    }
                    out.append(info)
            
            # Sort by downloads and limit results
            return sorted(out, key=lambda x: x['downloads'], reverse=True)[:limit]
            
        except Exception as e:
            self.console.print(f"[red]Failed to search models: {e}[/red]")
            return []

    def display_search_results(self, models: List[dict], query: str):
        """Display search results in a beautiful table with quantization detection"""
        if not models:
            self.console.print(f"[yellow]No models found matching '{query}'[/yellow]")
            return
        
        # Create main results table
        table = Table(
            title=f"🔍 Search Results for '{query}'", 
            box=box.ROUNDED, 
            title_style=COGNICLI_ACCENT
        )
        table.add_column("Model ID", style=COGNICLI_ACCENT, no_wrap=True)
        table.add_column("Downloads", style="green", justify="right")
        table.add_column("Likes", style="yellow", justify="right")
        table.add_column("Author", style="cyan")
        table.add_column("Tags", style="blue")
        table.add_column("GGUF Available", style="magenta")
        
        for model in models:
            # Check if GGUF files are available
            gguf_available = "❌"
            try:
                files = self.api.list_files(model['id'])
                gguf_files = [f for f in files if f.rfilename.endswith(".gguf")]
                if gguf_files:
                    gguf_available = f"✅ ({len(gguf_files)})"
            except:
                pass
            
            tags = ", ".join(model['tags'][:3]) if model['tags'] else "N/A"
            author = model.get('author', 'Unknown')
            
            table.add_row(
                model['id'], 
                f"{model['downloads']:,}", 
                f"{model['likes']:,}", 
                author,
                tags,
                gguf_available
            )
        
        self.console.print(table)
        
        # Show quantization options for GGUF models
        gguf_models = [m for m in models if "✅" in table.rows[models.index(m)][5]]
        if gguf_models:
            self.console.print(f"\n[dim]💡 Tip: Models with ✅ have GGUF files available. Use --files <model_id> to see quantization options.[/dim]")
            self.console.print(f"[dim]💡 Tip: Use --ollama pull <model_name>:<quantization> to pull specific quantizations from Ollama.[/dim]")

    def _format_size(self, nbytes: int) -> str:
        """Format file size with proper units"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if nbytes < 1024:
                return f"{nbytes:.1f} {unit}"
            nbytes /= 1024
        return f"{nbytes:.1f} TB"

    def load_model(self, model_id: str, **kwargs) -> bool:
        """Load a model with enhanced progress indication and error handling"""
        try:
            # Show loading status
            with self.console.status(f"[{COGNICLI_ACCENT}]Loading {model_id}...[/{COGNICLI_ACCENT}]", spinner="dots"):
                success = self.model_manager.load_model(model_id, **kwargs)
            
            if success:
                config = self.model_manager.get_current_config()
                if config:
                    self.console.print(f"[bold green]✅ Model loaded successfully![/bold green]")
                    self.console.print(f"[dim]Type: {config.model_type.title()}[/dim]")
                    self.console.print(f"[dim]Precision: {config.precision}[/dim]")
                    if torch.cuda.is_available():
                        self.console.print(f"[dim]GPU: Available[/dim]")
                    else:
                        self.console.print(f"[dim]GPU: Not available[/dim]")
                return True
            else:
                self.console.print(f"[red]❌ Failed to load model {model_id}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]❌ Error loading model: {e}[/red]")
            return False

    def generate_response(self, prompt: str, stream: bool = True, show_thinking: bool = True) -> str:
        """Generate response with enhanced error handling"""
        try:
            return self.response_generator.generate_response(prompt, stream, show_thinking)
        except Exception as e:
            self.console.print(f"[red]❌ Generation failed: {e}[/red]")
            return ""

    def benchmark_model(self) -> Dict[str, Any]:
        """Enhanced benchmark with comprehensive metrics"""
        if not self.model_manager.is_model_loaded():
            self.console.print("[red]No model loaded.[/red]")
            return {}
        
        try:
            config = self.model_manager.get_current_config()
            if not config:
                self.console.print("[red]Model configuration not found.[/red]")
                return {}
            
            self.console.print(f"[{COGNICLI_ACCENT}]Running benchmark on {config.name}...[/{COGNICLI_ACCENT}]")
            
            # Test prompts for different scenarios
            test_prompts = [
                "The quick brown fox jumps over the lazy dog.",
                "Python is a programming language that emphasizes code readability.",
                "Machine learning algorithms can process vast amounts of data efficiently."
            ]
            
            results = {
                "model": config.name,
                "type": config.model_type,
                "precision": config.precision,
                "runs": 5,
                "prompts": len(test_prompts),
                "total_tokens": 0,
                "total_time": 0,
                "prompt_results": []
            }
            
            for i, prompt in enumerate(test_prompts):
                self.console.print(f"[dim]Testing prompt {i+1}/{len(test_prompts)}: {prompt[:50]}...[/dim]")
                
                prompt_times = []
                prompt_tokens = 0
                
                for run in range(results["runs"]):
                    start_time = time.time()
                    
                    try:
                        if config.model_type == "gguf":
                            response = self.model_manager.current_model(
                                prompt=prompt, 
                                max_tokens=32, 
                                temperature=0.1
                            )
                            tokens = len(response['choices'][0]['text'].split())
                        else:
                            inputs = self.model_manager.current_tokenizer(prompt, return_tensors="pt")
                            input_ids = inputs["input_ids"].to(self.model_manager.current_model.device)
                            
                            with torch.no_grad():
                                outputs = self.model_manager.current_model.generate(
                                    input_ids=input_ids, 
                                    max_new_tokens=32,
                                    temperature=0.1
                                )
                            
                            response_text = self.model_manager.current_tokenizer.decode(
                                outputs[0][input_ids.shape[1]:], 
                                skip_special_tokens=True
                            )
                            tokens = len(response_text.split())
                        
                        end_time = time.time()
                        prompt_times.append(end_time - start_time)
                        prompt_tokens += tokens
                        
                    except Exception as e:
                        self.console.print(f"[red]Benchmark run {run+1} failed: {e}[/red]")
                        continue
                
                if prompt_times:
                    avg_time = np.mean(prompt_times)
                    std_time = np.std(prompt_times)
                    tokens_per_sec = prompt_tokens / avg_time if avg_time > 0 else 0
                    
                    results["prompt_results"].append({
                        "prompt": prompt,
                        "avg_time": avg_time,
                        "std_time": std_time,
                        "tokens_per_sec": tokens_per_sec,
                        "total_tokens": prompt_tokens
                    })
                    
                    results["total_time"] += avg_time * results["runs"]
                    results["total_tokens"] += prompt_tokens
            
            # Calculate overall metrics
            if results["prompt_results"]:
                overall_tokens_per_sec = results["total_tokens"] / results["total_time"] if results["total_time"] > 0 else 0
                results["overall_tokens_per_sec"] = overall_tokens_per_sec
                
                # Display results
                self.display_benchmark_results(results)
            
            return results
            
        except Exception as e:
            self.console.print(f"[red]Benchmark failed: {e}[/red]")
            return {}

    def display_benchmark_results(self, results: Dict[str, Any]):
        """Display benchmark results in a beautiful table"""
        # Overall results
        overall_table = Table(
            title="🏁 Overall Benchmark Results", 
            box=box.ROUNDED, 
            title_style=COGNICLI_ACCENT
        )
        overall_table.add_column("Metric", style=COGNICLI_ACCENT)
        overall_table.add_column("Value", style="green")
        
        overall_table.add_row("Model", results["model"])
        overall_table.add_row("Type", results["type"].title())
        overall_table.add_row("Precision", results["precision"])
        overall_table.add_row("Total Tokens", f"{results['total_tokens']:,}")
        overall_table.add_row("Total Time", f"{results['total_time']:.3f}s")
        overall_table.add_row("Overall Speed", f"{results.get('overall_tokens_per_sec', 0):.2f} tokens/sec")
        
        self.console.print(overall_table)
        self.console.print()
        
        # Detailed results by prompt
        if results["prompt_results"]:
            detail_table = Table(
                title="📊 Detailed Results by Prompt", 
                box=box.ROUNDED, 
                title_style=COGNICLI_ACCENT
            )
            detail_table.add_column("Prompt", style=COGNICLI_ACCENT, no_wrap=True)
            detail_table.add_column("Avg Time (s)", style="green")
            detail_table.add_column("Std Dev (s)", style="yellow")
            detail_table.add_column("Tokens/sec", style="cyan")
            detail_table.add_column("Total Tokens", style="magenta")
            
            for prompt_result in results["prompt_results"]:
                detail_table.add_row(
                    prompt_result["prompt"][:50] + "..." if len(prompt_result["prompt"]) > 50 else prompt_result["prompt"],
                    f"{prompt_result['avg_time']:.3f}",
                    f"{prompt_result['std_time']:.3f}",
                    f"{prompt_result['tokens_per_sec']:.2f}",
                    str(prompt_result['total_tokens'])
                )
            
            self.console.print(detail_table)

    def run_lm_eval(self, tasks="hellaswag", num_fewshot=0):
        """Run lm-eval-harness with enhanced error handling"""
        if not self.model_manager.is_model_loaded():
            self.console.print(f"[red]No model loaded. Use --model to load a model first.[/red]")
            return
        
        try:
            self.console.print(f"[{COGNICLI_ACCENT}]Running lm-eval-harness...[/{COGNICLI_ACCENT}]")
            
            # Install lm-eval if not available
            try:
                import lm_eval
                from lm_eval import evaluator
            except ImportError:
                self.console.print(f"[{COGNICLI_ACCENT}]Installing lm-eval-harness...[/{COGNICLI_ACCENT}]")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'lm-eval'])
                import lm_eval
                from lm_eval import evaluator
            
            config = self.model_manager.get_current_config()
            if not config:
                self.console.print("[red]Model configuration not found.[/red]")
                return
            
            # Configure model arguments
            if config.model_type == "gguf":
                lm_eval_model = "gguf"
                model_args = f"model_file={config.name}"
            else:
                lm_eval_model = "hf"
                model_args = f"pretrained={config.name},trust_remote_code=True"
                if torch.cuda.is_available():
                    model_args += ",device=cuda"
            
            # Run evaluation
            with self.console.status(f"[{COGNICLI_ACCENT}]Evaluating on {tasks}...[/{COGNICLI_ACCENT}]"):
                results = evaluator.simple_evaluate(
                    model=lm_eval_model,
                    model_args=model_args,
                    tasks=tasks,
                    num_fewshot=num_fewshot,
                    batch_size=1,
                )
            
            # Display results
            self.display_lm_eval_results(results, tasks)
            
        except Exception as e:
            self.console.print(f"[red]Error running lm-eval: {e}[/red]")

    def display_lm_eval_results(self, results: Dict[str, Any], tasks: str):
        """Display lm-eval results in a beautiful table"""
        table = Table(
            title=f"📊 LM Evaluation Results: {tasks}", 
            box=box.ROUNDED, 
            title_style=COGNICLI_ACCENT
        )
        table.add_column("Task", style=COGNICLI_ACCENT)
        table.add_column("Metric", style="magenta")
        table.add_column("Value", style="green")
        
        for task, data in results["results"].items():
            for metric, value in data.items():
                if isinstance(value, (int, float)):
                    val = f"{value:.4f}" if isinstance(value, float) else str(value)
                    table.add_row(task, metric, val)
        
        self.console.print(table)
        
        # Show summary if available
        if "versions" in results:
            self.console.print(f"\n[dim]Evaluation completed with lm-eval version: {results['versions'].get('lm-eval', 'Unknown')}[/dim]")

    def handle_ollama_operations(self, operation: str, model_name: str = None, quantization: str = None):
        """Handle Ollama operations: list, search, pull"""
        try:
            if operation == "list":
                self._list_ollama_models()
            elif operation == "search" and model_name:
                self._search_ollama_models(model_name)
            elif operation == "pull" and model_name:
                self._pull_ollama_model(model_name, quantization)
            elif operation == "quantizations":
                self.ollama_manager.show_quantization_help()
            else:
                self.console.print(f"[red]Invalid Ollama operation: {operation}[/red]")
                self.console.print(f"[dim]Valid operations: list, search <query>, pull <model>[:<quantization>], quantizations[/dim]")
        except Exception as e:
            self.console.print(f"[red]Error in Ollama operation: {e}[/red]")

    def _list_ollama_models(self):
        """List all available Ollama models"""
        self.console.print(f"[{COGNICLI_ACCENT}]Listing Ollama models...[/{COGNICLI_ACCENT}]")
        models = self.ollama_manager.list_models()
        
        if not models:
            return
        
        table = Table(
            title="🦙 Available Ollama Models", 
            box=box.ROUNDED, 
            title_style=COGNICLI_ACCENT
        )
        table.add_column("Model Name", style=COGNICLI_ACCENT)
        table.add_column("Size", style="green")
        table.add_column("Modified", style="yellow")
        table.add_column("Digest", style="cyan")
        
        for model in models:
            size = self._format_size(model.get("size", 0))
            modified = model.get("modified_at", "Unknown")
            if modified != "Unknown":
                try:
                    # Parse ISO timestamp
                    from datetime import datetime
                    dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                    modified = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            table.add_row(
                model["name"],
                size,
                modified,
                model["digest"]
            )
        
        self.console.print(table)
        self.console.print(f"\n[dim]💡 Tip: Use --ollama pull <model_name>:<quantization> to pull specific quantizations[/dim]")
        self.console.print(f"[dim]💡 Tip: Use --ollama quantizations to see available quantization options[/dim]")

    def _search_ollama_models(self, query: str):
        """Search for Ollama models"""
        self.console.print(f"[{COGNICLI_ACCENT}]Searching Ollama for '{query}'...[/{COGNICLI_ACCENT}]")
        models = self.ollama_manager.search_models(query)
        
        if not models:
            self.console.print(f"[yellow]No Ollama models found matching '{query}'[/yellow]")
            return
        
        table = Table(
            title=f"🔍 Ollama Search Results for '{query}'", 
            box=box.ROUNDED, 
            title_style=COGNICLI_ACCENT
        )
        table.add_column("Model Name", style=COGNICLI_ACCENT)
        table.add_column("Description", style="green")
        table.add_column("Downloads", style="yellow", justify="right")
        table.add_column("Likes", style="cyan", justify="right")
        table.add_column("Tags", style="blue")
        table.add_column("Size", style="magenta")
        
        for model in models:
            tags = ", ".join(model.get("tags", [])[:3])
            size = self._format_size(model.get("size", 0))
            
            table.add_row(
                model["name"],
                model.get("description", "No description")[:50] + "..." if len(model.get("description", "")) > 50 else model.get("description", "No description"),
                f"{model.get('downloads', 0):,}",
                f"{model.get('likes', 0):,}",
                tags,
                size
            )
        
        self.console.print(table)
        self.console.print(f"\n[dim]💡 Tip: Use --ollama pull <model_name> to download a model[/dim]")

    def _pull_ollama_model(self, model_name: str, quantization: str = None):
        """Pull an Ollama model"""
        if quantization:
            full_name = f"{model_name}:{quantization}"
        else:
            full_name = model_name
        
        self.console.print(f"[{COGNICLI_ACCENT}]Pulling Ollama model: {full_name}[/{COGNICLI_ACCENT}]")
        
        success = self.ollama_manager.pull_model(model_name, quantization)
        if success:
            self.console.print(f"[bold green]✅ Successfully pulled {full_name}[/bold green]")
            self.console.print(f"[dim]💡 Tip: You can now use this model with Ollama or load it directly[/dim]")
        else:
            self.console.print(f"[red]❌ Failed to pull {full_name}[/red]")
            self.console.print(f"[dim]💡 Tip: Check if Ollama is running and the model name is correct[/dim]")

    def show_quantization_options(self):
        """Show available quantization options for GGUF models"""
        self.ollama_manager.show_quantization_help()

class OllamaManager:
    """Manage Ollama operations including listing, pulling, and searching models"""
    
    def __init__(self, console: Console):
        self.console = console
        self.base_url = "http://localhost:11434"
        self.available_quantizations = [
            "q4_0", "q4_1", "q4_K_M", "q4_K_S", "q5_0", "q5_1", "q5_K_M", "q5_K_S",
            "q8_0", "f16", "f32"
        ]
    
    def is_ollama_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all available Ollama models"""
        try:
            if not self.is_ollama_running():
                self.console.print("[red]❌ Ollama service is not running. Start Ollama first.[/red]")
                return []
            
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("models", []):
                    model_info = {
                        "name": model.get("name", "Unknown"),
                        "size": model.get("size", 0),
                        "modified_at": model.get("modified_at", "Unknown"),
                        "digest": model.get("digest", "Unknown")[:8] if model.get("digest") else "Unknown"
                    }
                    models.append(model_info)
                return models
            else:
                self.console.print(f"[red]Failed to list Ollama models: {response.status_code}[/red]")
                return []
        except Exception as e:
            self.console.print(f"[red]Error listing Ollama models: {e}[/red]")
            return []
    
    def search_models(self, query: str) -> List[Dict[str, Any]]:
        """Search for Ollama models"""
        try:
            if not self.is_ollama_running():
                self.console.print("[red]❌ Ollama service is not running. Start Ollama first.[/red]")
                return []
            
            # Use Ollama's search API
            response = requests.get(f"{self.base_url}/api/search", params={"q": query})
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("models", []):
                    model_info = {
                        "name": model.get("name", "Unknown"),
                        "description": model.get("description", "No description"),
                        "downloads": model.get("downloads", 0),
                        "likes": model.get("likes", 0),
                        "tags": model.get("tags", []),
                        "size": model.get("size", 0)
                    }
                    models.append(model_info)
                return models
            else:
                self.console.print(f"[red]Failed to search Ollama models: {response.status_code}[/red]")
                return []
        except Exception as e:
            self.console.print(f"[red]Error searching Ollama models: {e}[/red]")
            return []
    
    def pull_model(self, model_name: str, quantization: str = None) -> bool:
        """Pull a model from Ollama"""
        try:
            if not self.is_ollama_running():
                self.console.print("[red]❌ Ollama service is not running. Start Ollama first.[/red]")
                return False
            
            # If quantization is specified, append it to model name
            if quantization:
                full_model_name = f"{model_name}:{quantization}"
            else:
                full_model_name = model_name
            
            self.console.print(f"[{COGNICLI_ACCENT}]Pulling Ollama model: {full_model_name}[/{COGNICLI_ACCENT}]")
            
            # Start pull request
            response = requests.post(f"{self.base_url}/api/pull", json={"name": full_model_name})
            if response.status_code == 200:
                self.console.print(f"[bold green]✅ Successfully pulled {full_model_name}[/bold green]")
                return True
            else:
                self.console.print(f"[red]❌ Failed to pull {full_model_name}: {response.status_code}[/red]")
                return False
        except Exception as e:
            self.console.print(f"[red]Error pulling Ollama model: {e}[/red]")
            return False
    
    def get_available_quantizations(self) -> List[str]:
        """Get list of available quantization options"""
        return self.available_quantizations.copy()
    
    def show_quantization_help(self):
        """Show help for quantization options"""
        help_text = f"""
[bold {COGNICLI_ACCENT}]Available GGUF Quantizations:[/bold {COGNICLI_ACCENT}]

[green]4-bit Quantizations:[/green]
• [cyan]q4_0[/cyan] - Standard 4-bit quantization (balanced)
• [cyan]q4_1[/cyan] - Improved 4-bit quantization
• [cyan]q4_K_M[/cyan] - 4-bit K-quants with medium quality
• [cyan]q4_K_S[/cyan] - 4-bit K-quants with small size

[green]5-bit Quantizations:[/green]
• [cyan]q5_0[/cyan] - Standard 5-bit quantization
• [cyan]q5_1[/cyan] - Improved 5-bit quantization
• [cyan]q5_K_M[/cyan] - 5-bit K-quants with medium quality
• [cyan]q5_K_S[/cyan] - 5-bit K-quants with small size

[green]8-bit and Full Precision:[/green]
• [cyan]q8_0[/cyan] - 8-bit quantization (high quality)
• [cyan]f16[/cyan] - Half precision (16-bit)
• [cyan]f32[/cyan] - Full precision (32-bit)

[dim]Usage Examples:[/dim]
• [yellow]--ollama pull llama2:q4_K_M[/yellow] - Pull 4-bit K-quants version
• [yellow]--ollama pull codellama:q8_0[/yellow] - Pull 8-bit version
• [yellow]--model path/to/model.gguf --quantization q4_K_M[/yellow] - Load specific quantization
"""
        self.console.print(Panel(help_text, title="🔧 Quantization Guide", border_style=COGNICLI_ACCENT))

def main():
    parser = argparse.ArgumentParser(
        description="CogniCLI - Premium AI Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cognicli --list llama                    # List Llama models
  cognicli --search llama2                 # Search for llama2 models
  cognicli --info microsoft/DialoGPT-medium # Show model info
  cognicli --model gpt2 --chat            # Start chat with GPT-2
  cognicli --model gpt2 --generate "Hello" # Generate single response
  cognicli --model gpt2 --benchmark       # Run performance benchmark
  cognicli --model gpt2 --lm_eval mmlu   # Run evaluation on MMLU
  cognicli --ollama list                  # List available Ollama models
  cognicli --ollama search llama2         # Search Ollama for llama2
  cognicli --ollama pull llama2:q4_K_M   # Pull specific quantization
  cognicli --ollama quantizations         # Show quantization options
        """
    )
    
    # Model management
    parser.add_argument('--model', type=str, help='Model to load (Hugging Face model ID)')
    parser.add_argument('--type', choices=['bf16', 'fp16', 'fp32', 'q4', 'q8'], default='auto', 
                       help='Model precision (default: auto)')
    parser.add_argument('--gguf-file', type=str, help='Specific GGUF file to use')
    parser.add_argument('--context', type=int, default=2048, help='Context length (default: 2048)')
    
    # Generation parameters
    parser.add_argument('--no-think', action='store_true', help='Disable reasoning traces')
    parser.add_argument('--no-stream', action='store_true', help='Disable streaming output')
    parser.add_argument('--temperature', type=float, default=0.7, help='Sampling temperature (default: 0.7)')
    parser.add_argument('--max-tokens', type=int, default=512, help='Maximum tokens to generate (default: 512)')
    parser.add_argument('--top-p', type=float, default=0.95, help='Top-p sampling (default: 0.95)')
    
    # Modes
    parser.add_argument('--chat', action='store_true', help='Start interactive chat mode')
    parser.add_argument('--generate', type=str, help='Generate response for prompt')
    
    # Analysis and benchmarking
    parser.add_argument('--benchmark', action='store_true', help='Run model benchmark')
    parser.add_argument('--lm_eval', type=str, nargs='?', const="hellaswag", 
                       help='Run lm-eval-harness: e.g. --lm_eval mmlu or --lm_eval all')
    
    # Model exploration
    face_parser = parser.add_mutually_exclusive_group()
    face_parser.add_argument('--list', type=str, nargs='?', const='', 
                            help='List models (optional filter)')
    face_parser.add_argument('--info', type=str, help='Show detailed model info')
    face_parser.add_argument('--files', type=str, help='Show model files')
    face_parser.add_argument('--search', type=str, help='Search for models on Hugging Face')
    
    # Ollama integration
    ollama_group = parser.add_argument_group('Ollama Operations')
    ollama_group.add_argument('--ollama', nargs='+', metavar='OPERATION',
                             help='Ollama operations: list, search <query>, pull <model>[:<quantization>], quantizations')
    
    # Quantization options
    parser.add_argument('--quantization', type=str, choices=[
        'q4_0', 'q4_1', 'q4_K_M', 'q4_K_S', 'q5_0', 'q5_1', 'q5_K_M', 'q5_K_S',
        'q8_0', 'f16', 'f32'
    ], help='Specific quantization for GGUF models')
    
    # Output and configuration
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    parser.add_argument('--save-benchmark', type=str, help='Save benchmark results to file')
    parser.add_argument('--config', type=str, help='Load configuration from file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--version', action='version', version='CogniCLI v2.0.8 - Premium Edition')
    
    args = parser.parse_args()

    # Initialize CLI
    cli = CogniCLI()
    
    # Handle model exploration commands (show logo only for these)
    if args.list is not None:
        cli.show_logo()
        models = cli.list_models(args.list)
        if args.json:
            print(json.dumps(models, indent=2, default=str))
        else:
            table = Table(
                title="Available Models", 
                box=box.ROUNDED, 
                title_style=COGNICLI_ACCENT
            )
            table.add_column("Model ID", style=COGNICLI_ACCENT, no_wrap=True)
            table.add_column("Downloads", style="green", justify="right")
            table.add_column("Likes", style="yellow", justify="right")
            table.add_column("Tags", style="blue")
            table.add_column("Last Modified", style="cyan")
            
            for model in models[:20]:  # Show top 20 models
                tags = ", ".join(model['tags'][:3]) if model['tags'] else "N/A"
                last_modified = model.get('last_modified', 'Unknown')
                if last_modified != 'Unknown':
                    last_modified = last_modified.strftime('%Y-%m-%d') if hasattr(last_modified, 'strftime') else str(last_modified)
                
                table.add_row(
                    model['id'], 
                    f"{model['downloads']:,}", 
                    f"{model['likes']:,}", 
                    tags,
                    last_modified
                )
            cli.console.print(table)
        return

    if args.info:
        cli.show_logo()
        cli.show_model_info(args.info)
        return

    if args.files:
        cli.show_logo()
        cli.show_model_files(args.files)
        return

    if args.search:
        cli.show_logo()
        models = cli.search_models(args.search, limit=20)
        if args.json:
            print(json.dumps(models, indent=2, default=str))
        else:
            cli.display_search_results(models, args.search)
        return

    # Handle Ollama operations
    if args.ollama:
        cli.show_logo()
        ollama_args = args.ollama
        
        if len(ollama_args) == 1:
            if ollama_args[0] == "list":
                cli.handle_ollama_operations("list")
            elif ollama_args[0] == "quantizations":
                cli.handle_ollama_operations("quantizations")
            else:
                cli.console.print(f"[red]Invalid Ollama operation: {ollama_args[0]}[/red]")
                cli.console.print(f"[dim]Valid operations: list, search <query>, pull <model>[:<quantization>], quantizations[/dim]")
        elif len(ollama_args) == 2:
            if ollama_args[0] == "search":
                cli.handle_ollama_operations("search", ollama_args[1])
            elif ollama_args[0] == "pull":
                cli.handle_ollama_operations("pull", ollama_args[1])
            else:
                cli.console.print(f"[red]Invalid Ollama operation: {ollama_args[0]}[/red]")
        elif len(ollama_args) == 3 and ollama_args[0] == "pull":
            # Handle pull with quantization: --ollama pull llama2 q4_K_M
            cli.handle_ollama_operations("pull", ollama_args[1], ollama_args[2])
        else:
            cli.console.print(f"[red]Invalid Ollama arguments: {' '.join(ollama_args)}[/red]")
            cli.console.print(f"[dim]Examples:[/dim]")
            cli.console.print(f"[dim]  --ollama list[/dim]")
            cli.console.print(f"[dim]  --ollama search llama2[/dim]")
            cli.console.print(f"[dim]  --ollama pull llama2[/dim]")
            cli.console.print(f"[dim]  --ollama pull llama2 q4_K_M[/dim]")
            cli.console.print(f"[dim]  --ollama quantizations[/dim]")
        return

    # Version is handled automatically by argparse

    # Load model if specified
    loaded_model = False
    if args.model:
        model_kwargs = {
            'model_type': "gguf" if args.gguf_file else "auto",
            'precision': args.type,
            'gguf_file': args.gguf_file,
            'context_length': args.context,
            'temperature': args.temperature,
            'top_p': args.top_p,
            'max_tokens': args.max_tokens
        }
        
        # Add quantization if specified
        if args.quantization:
            model_kwargs['quantization'] = args.quantization
            if args.gguf_file:
                # For GGUF files, we can't change quantization, so warn user
                cli.console.print(f"[yellow]⚠️  Quantization {args.quantization} specified but using existing GGUF file[/yellow]")
        
        loaded_model = cli.load_model(args.model, **model_kwargs)
        
        if not loaded_model:
            cli.console.print(f"[red]Failed to load model {args.model}. Exiting.[/red]")
            return

    # Handle analysis commands
    if args.benchmark:
        if not loaded_model:
            cli.console.print(f"[red]No model loaded. Use --model to load a model first.[/red]")
            return
            
        results = cli.benchmark_model()
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        if args.save_benchmark:
            try:
                with open(args.save_benchmark, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                cli.console.print(f"[green]✅ Benchmark results saved to {args.save_benchmark}[/green]")
            except Exception as e:
                cli.console.print(f"[red]Failed to save benchmark results: {e}[/red]")
        return

    if args.lm_eval:
        if not loaded_model:
            cli.console.print(f"[red]No model loaded. Use --model to load a model first.[/red]")
            return
            
        tag = args.lm_eval.strip().lower() if args.lm_eval else "hellaswag"
        if tag == "all":
            tasks = ",".join(BENCHMARK_PRESETS["all"])
        elif tag in BENCHMARK_PRESETS:
            tasks = ",".join(BENCHMARK_PRESETS[tag])
        else:
            tasks = tag
            
        cli.run_lm_eval(tasks=tasks)
        return

    # Handle generation commands
    if args.generate:
        if not loaded_model:
            cli.console.print(f"[red]No model loaded. Use --model to load a model first.[/red]")
            return
            
        cli.generate_response(
            args.generate,
            stream=not args.no_stream,
            show_thinking=not args.no_think
        )
        return

    # Interactive chat mode
    if args.chat:
        if not loaded_model:
            cli.console.print(f"[red]No model loaded. Use --model to load a model first.[/red]")
            return
            
        cli.start_interactive_chat()
        return

    # Default behavior: Show logo and welcome, then start interactive mode
    cli.show_logo()
    cli.show_welcome_message(loaded_model)
    cli.start_interactive_mode(loaded_model)

class CogniCLI:
    """Enhanced CogniCLI with premium features and robust error handling"""
    
    def __init__(self):
        self.console = Console()
        self.model_manager = ModelManager(self.console)
        self.response_generator = ResponseGenerator(self.model_manager, self.console)
        self.ollama_manager = OllamaManager(self.console)
        self.api = HfApi()
        self.cache_dir = Path.home() / '.cognicli'
        self.cache_dir.mkdir(exist_ok=True)
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.console.print(f"\n[yellow]Received signal {signum}, shutting down gracefully...[/yellow]")
        if self.model_manager.is_model_loaded():
            self.model_manager.unload_current_model()
        sys.exit(0)

    def show_logo(self):
        """Display the enhanced logo with better formatting"""
        logo_text = Text(LOGO)
        logo_text.stylize(f"bold {COGNICLI_ACCENT}")
        
        # Add version and status info
        version_text = Text("v2.0.8 - Premium Edition", style="dim")
        status_text = Text("🚀 Enhanced • Robust • Premium", style="green")
        
        panel = Panel(
            Align.center(logo_text),
            title="CogniCLI",
            subtitle="Premium AI Command Line Interface",
            border_style=COGNICLI_ACCENT,
            padding=(1, 4),
        )
        
        self.console.print(Align.center(panel))
        self.console.print(Align.center(version_text))
        self.console.print(Align.center(status_text))
        self.console.print()

    def list_models(self, filter_term: str = "") -> List[dict]:
        """List models with enhanced filtering and display"""
        try:
            with self.console.status(f"[{COGNICLI_ACCENT}]Searching models...[/{COGNICLI_ACCENT}]"):
                models = self.api.list_models(filter="text-generation")
            
            out = []
            for model in models:
                if filter_term.lower() in model.modelId.lower():
                    info = {
                        "id": model.modelId,
                        "downloads": getattr(model, "downloads", 0),
                        "likes": getattr(model, "likes", 0),
                        "tags": getattr(model, "tags", []),
                        "last_modified": getattr(model, "lastModified", None),
                    }
                    out.append(info)
            
            return sorted(out, key=lambda x: x['downloads'], reverse=True)
            
        except Exception as e:
            self.console.print(f"[red]Failed to list models: {e}[/red]")
            return []

    def show_model_info(self, model_id: str):
        """Show detailed model information with enhanced display"""
        try:
            with self.console.status(f"[{COGNICLI_ACCENT}]Fetching model info...[/{COGNICLI_ACCENT}]"):
                info = self.api.model_info(model_id)
            
            # Create a comprehensive info panel
            info_content = f"""
[bold]{info.modelId}[/bold]

[dim]📊 Statistics:[/dim]
• [green]Downloads:[/green] {info.downloads:,}
• [yellow]Likes:[/yellow] {info.likes:,}
• [blue]Tags:[/blue] {', '.join(info.tags[:10])}{'...' if len(info.tags) > 10 else ''}

[dim]📝 Description:[/dim]
{info.cardData.get('summary', 'No summary available.')}

[dim]🔧 Model Details:[/dim]
• [cyan]Author:[/cyan] {info.author or 'Unknown'}
• [cyan]Pipeline:[/cyan] {', '.join(info.pipeline_tag) if hasattr(info, 'pipeline_tag') else 'Unknown'}
• [cyan]License:[/cyan] {info.license or 'Unknown'}
"""
            
            panel = Panel(
                info_content,
                title=f"Model Information: {model_id}",
                border_style=COGNICLI_ACCENT,
                padding=(1, 2),
            )
            self.console.print(panel)
            
        except Exception as e:
            self.console.print(f"[red]Failed to get info for model: {e}[/red]")

    def show_model_files(self, model_id: str):
        """Show model files with enhanced display and GGUF detection"""
        try:
            with self.console.status(f"[{COGNICLI_ACCENT}]Fetching model files...[/{COGNICLI_ACCENT}]"):
                files = self.api.list_files(model_id)
            
            # Separate GGUF files from others
            gguf_files = [f for f in files if f.rfilename.endswith(".gguf")]
            other_files = [f for f in files if not f.rfilename.endswith(".gguf")]
            
            # Create tables
            if gguf_files:
                gguf_table = Table(
                    title=f"🦙 GGUF Files for {model_id}", 
                    box=box.ROUNDED, 
                    title_style=COGNICLI_ACCENT
                )
                gguf_table.add_column("File Name", style=COGNICLI_ACCENT)
                gguf_table.add_column("Size", style="green")
                gguf_table.add_column("SHA256", style="yellow")
                gguf_table.add_column("Type", style="cyan")
                
                for f in gguf_files:
                    # Determine quantization type from filename
                    q_type = "Unknown"
                    if "q4" in f.rfilename.lower():
                        q_type = "4-bit"
                    elif "q8" in f.rfilename.lower():
                        q_type = "8-bit"
                    elif "q5" in f.rfilename.lower():
                        q_type = "5-bit"
                    
                    gguf_table.add_row(f.rfilename, self._format_size(f.size), f.sha256[:8], q_type)
                
                self.console.print(gguf_table)
                self.console.print()
            
            if other_files:
                other_table = Table(
                    title=f"📁 Other Files for {model_id}", 
                    box=box.ROUNDED, 
                    title_style=COGNICLI_ACCENT
                )
                other_table.add_column("File Name", style=COGNICLI_ACCENT)
                other_table.add_column("Size", style="green")
                other_table.add_column("SHA256", style="yellow")
                
                for f in other_files:
                    other_table.add_row(f.rfilename, self._format_size(f.size), f.sha256[:8])
                
                self.console.print(other_table)
                
        except Exception as e:
            self.console.print(f"[red]Failed to get files for model: {e}[/red]")

    def search_models(self, query: str, limit: int = 20) -> List[dict]:
        """Search for models on Hugging Face with enhanced filtering and display"""
        try:
            with self.console.status(f"[{COGNICLI_ACCENT}]Searching for '{query}'...[/{COGNICLI_ACCENT}]"):
                # Search for models with the query
                models = self.api.list_models(
                    filter="text-generation",
                    search=query,
                    limit=limit * 2  # Get more to filter better
                )
            
            out = []
            for model in models:
                # Enhanced filtering based on query
                query_terms = query.lower().split()
                model_id_lower = model.modelId.lower()
                
                # Check if all query terms are present in model ID
                if all(term in model_id_lower for term in query_terms):
                    info = {
                        "id": model.modelId,
                        "downloads": getattr(model, "downloads", 0),
                        "likes": getattr(model, "likes", 0),
                        "tags": getattr(model, "tags", []),
                        "last_modified": getattr(model, "lastModified", None),
                        "author": getattr(model, "author", "Unknown"),
                        "pipeline_tag": getattr(model, "pipeline_tag", []),
                        "card_data": getattr(model, "cardData", {})
                    }
                    out.append(info)
            
            # Sort by downloads and limit results
            return sorted(out, key=lambda x: x['downloads'], reverse=True)[:limit]
            
        except Exception as e:
            self.console.print(f"[red]Failed to search models: {e}[/red]")
            return []

    def display_search_results(self, models: List[dict], query: str):
        """Display search results in a beautiful table with quantization detection"""
        if not models:
            self.console.print(f"[yellow]No models found matching '{query}'[/yellow]")
            return
        
        # Create main results table
        table = Table(
            title=f"🔍 Search Results for '{query}'", 
            box=box.ROUNDED, 
            title_style=COGNICLI_ACCENT
        )
        table.add_column("Model ID", style=COGNICLI_ACCENT, no_wrap=True)
        table.add_column("Downloads", style="green", justify="right")
        table.add_column("Likes", style="yellow", justify="right")
        table.add_column("Author", style="cyan")
        table.add_column("Tags", style="blue")
        table.add_column("GGUF Available", style="magenta")
        
        for model in models:
            # Check if GGUF files are available
            gguf_available = "❌"
            try:
                files = self.api.list_files(model['id'])
                gguf_files = [f for f in files if f.rfilename.endswith(".gguf")]
                if gguf_files:
                    gguf_available = f"✅ ({len(gguf_files)})"
            except:
                pass
            
            tags = ", ".join(model['tags'][:3]) if model['tags'] else "N/A"
            author = model.get('author', 'Unknown')
            
            table.add_row(
                model['id'], 
                f"{model['downloads']:,}", 
                f"{model['likes']:,}", 
                author,
                tags,
                gguf_available
            )
        
        self.console.print(table)
        
        # Show quantization options for GGUF models
        gguf_models = [m for m in models if "✅" in table.rows[models.index(m)][5]]
        if gguf_models:
            self.console.print(f"\n[dim]💡 Tip: Models with ✅ have GGUF files available. Use --files <model_id> to see quantization options.[/dim]")
            self.console.print(f"[dim]💡 Tip: Use --ollama pull <model_name>:<quantization> to pull specific quantizations from Ollama.[/dim]")

    def _format_size(self, nbytes: int) -> str:
        """Format file size with proper units"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if nbytes < 1024:
                return f"{nbytes:.1f} {unit}"
            nbytes /= 1024
        return f"{nbytes:.1f} TB"

    def load_model(self, model_id: str, **kwargs) -> bool:
        """Load a model with enhanced progress indication and error handling"""
        try:
            # Show loading status
            with self.console.status(f"[{COGNICLI_ACCENT}]Loading {model_id}...[/{COGNICLI_ACCENT}]", spinner="dots"):
                success = self.model_manager.load_model(model_id, **kwargs)
            
            if success:
                config = self.model_manager.get_current_config()
                if config:
                    self.console.print(f"[bold green]✅ Model loaded successfully![/bold green]")
                    self.console.print(f"[dim]Type: {config.model_type.title()}[/dim]")
                    self.console.print(f"[dim]Precision: {config.precision}[/dim]")
                    if torch.cuda.is_available():
                        self.console.print(f"[dim]GPU: Available[/dim]")
                    else:
                        self.console.print(f"[dim]GPU: Not available[/dim]")
                return True
            else:
                self.console.print(f"[red]❌ Failed to load model {model_id}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]❌ Error loading model: {e}[/red]")
            return False

    def generate_response(self, prompt: str, stream: bool = True, show_thinking: bool = True) -> str:
        """Generate response with enhanced error handling"""
        try:
            return self.response_generator.generate_response(prompt, stream, show_thinking)
        except Exception as e:
            self.console.print(f"[red]❌ Generation failed: {e}[/red]")
            return ""

    def benchmark_model(self) -> Dict[str, Any]:
        """Enhanced benchmark with comprehensive metrics"""
        if not self.model_manager.is_model_loaded():
            self.console.print("[red]No model loaded.[/red]")
            return {}
        
        try:
            config = self.model_manager.get_current_config()
            if not config:
                self.console.print("[red]Model configuration not found.[/red]")
                return {}
            
            self.console.print(f"[{COGNICLI_ACCENT}]Running benchmark on {config.name}...[/{COGNICLI_ACCENT}]")
            
            # Test prompts for different scenarios
            test_prompts = [
                "The quick brown fox jumps over the lazy dog.",
                "Python is a programming language that emphasizes code readability.",
                "Machine learning algorithms can process vast amounts of data efficiently."
            ]
            
            results = {
                "model": config.name,
                "type": config.model_type,
                "precision": config.precision,
                "runs": 5,
                "prompts": len(test_prompts),
                "total_tokens": 0,
                "total_time": 0,
                "prompt_results": []
            }
            
            for i, prompt in enumerate(test_prompts):
                self.console.print(f"[dim]Testing prompt {i+1}/{len(test_prompts)}: {prompt[:50]}...[/dim]")
                
                prompt_times = []
                prompt_tokens = 0
                
                for run in range(results["runs"]):
                    start_time = time.time()
                    
                    try:
                        if config.model_type == "gguf":
                            response = self.model_manager.current_model(
                                prompt=prompt, 
                                max_tokens=32, 
                                temperature=0.1
                            )
                            tokens = len(response['choices'][0]['text'].split())
                        else:
                            inputs = self.model_manager.current_tokenizer(prompt, return_tensors="pt")
                            input_ids = inputs["input_ids"].to(self.model_manager.current_model.device)
                            
                            with torch.no_grad():
                                outputs = self.model_manager.current_model.generate(
                                    input_ids=input_ids, 
                                    max_new_tokens=32,
                                    temperature=0.1
                                )
                            
                            response_text = self.model_manager.current_tokenizer.decode(
                                outputs[0][input_ids.shape[1]:], 
                                skip_special_tokens=True
                            )
                            tokens = len(response_text.split())
                        
                        end_time = time.time()
                        prompt_times.append(end_time - start_time)
                        prompt_tokens += tokens
                        
                    except Exception as e:
                        self.console.print(f"[red]Benchmark run {run+1} failed: {e}[/red]")
                        continue
                
                if prompt_times:
                    avg_time = np.mean(prompt_times)
                    std_time = np.std(prompt_times)
                    tokens_per_sec = prompt_tokens / avg_time if avg_time > 0 else 0
                    
                    results["prompt_results"].append({
                        "prompt": prompt,
                        "avg_time": avg_time,
                        "std_time": std_time,
                        "tokens_per_sec": tokens_per_sec,
                        "total_tokens": prompt_tokens
                    })
                    
                    results["total_time"] += avg_time * results["runs"]
                    results["total_tokens"] += prompt_tokens
            
            # Calculate overall metrics
            if results["prompt_results"]:
                overall_tokens_per_sec = results["total_tokens"] / results["total_time"] if results["total_time"] > 0 else 0
                results["overall_tokens_per_sec"] = overall_tokens_per_sec
                
                # Display results
                self.display_benchmark_results(results)
            
            return results
            
        except Exception as e:
            self.console.print(f"[red]Benchmark failed: {e}[/red]")
            return {}

    def display_benchmark_results(self, results: Dict[str, Any]):
        """Display benchmark results in a beautiful table"""
        # Overall results
        overall_table = Table(
            title="🏁 Overall Benchmark Results", 
            box=box.ROUNDED, 
            title_style=COGNICLI_ACCENT
        )
        overall_table.add_column("Metric", style=COGNICLI_ACCENT)
        overall_table.add_column("Value", style="green")
        
        overall_table.add_row("Model", results["model"])
        overall_table.add_row("Type", results["type"].title())
        overall_table.add_row("Precision", results["precision"])
        overall_table.add_row("Total Tokens", f"{results['total_tokens']:,}")
        overall_table.add_row("Total Time", f"{results['total_time']:.3f}s")
        overall_table.add_row("Overall Speed", f"{results.get('overall_tokens_per_sec', 0):.2f} tokens/sec")
        
        self.console.print(overall_table)
        self.console.print()
        
        # Detailed results by prompt
        if results["prompt_results"]:
            detail_table = Table(
                title="📊 Detailed Results by Prompt", 
                box=box.ROUNDED, 
                title_style=COGNICLI_ACCENT
            )
            detail_table.add_column("Prompt", style=COGNICLI_ACCENT, no_wrap=True)
            detail_table.add_column("Avg Time (s)", style="green")
            detail_table.add_column("Std Dev (s)", style="yellow")
            detail_table.add_column("Tokens/sec", style="cyan")
            detail_table.add_column("Total Tokens", style="magenta")
            
            for prompt_result in results["prompt_results"]:
                detail_table.add_row(
                    prompt_result["prompt"][:50] + "..." if len(prompt_result["prompt"]) > 50 else prompt_result["prompt"],
                    f"{prompt_result['avg_time']:.3f}",
                    f"{prompt_result['std_time']:.3f}",
                    f"{prompt_result['tokens_per_sec']:.2f}",
                    str(prompt_result['total_tokens'])
                )
            
            self.console.print(detail_table)

    def run_lm_eval(self, tasks="hellaswag", num_fewshot=0):
        """Run lm-eval-harness with enhanced error handling"""
        if not self.model_manager.is_model_loaded():
            self.console.print(f"[red]No model loaded. Use --model to load a model first.[/red]")
            return
        
        try:
            self.console.print(f"[{COGNICLI_ACCENT}]Running lm-eval-harness...[/{COGNICLI_ACCENT}]")
            
            # Install lm-eval if not available
            try:
                import lm_eval
                from lm_eval import evaluator
            except ImportError:
                self.console.print(f"[{COGNICLI_ACCENT}]Installing lm-eval-harness...[/{COGNICLI_ACCENT}]")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'lm-eval'])
                import lm_eval
                from lm_eval import evaluator
            
            config = self.model_manager.get_current_config()
            if not config:
                self.console.print("[red]Model configuration not found.[/red]")
                return
            
            # Configure model arguments
            if config.model_type == "gguf":
                lm_eval_model = "gguf"
                model_args = f"model_file={config.name}"
            else:
                lm_eval_model = "hf"
                model_args = f"pretrained={config.name},trust_remote_code=True"
                if torch.cuda.is_available():
                    model_args += ",device=cuda"
            
            # Run evaluation
            with self.console.status(f"[{COGNICLI_ACCENT}]Evaluating on {tasks}...[/{COGNICLI_ACCENT}]"):
                results = evaluator.simple_evaluate(
                    model=lm_eval_model,
                    model_args=model_args,
                    tasks=tasks,
                    num_fewshot=num_fewshot,
                    batch_size=1,
                )
            
            # Display results
            self.display_lm_eval_results(results, tasks)
            
        except Exception as e:
            self.console.print(f"[red]Error running lm-eval: {e}[/red]")

    def display_lm_eval_results(self, results: Dict[str, Any], tasks: str):
        """Display lm-eval results in a beautiful table"""
        table = Table(
            title=f"📊 LM Evaluation Results: {tasks}", 
            box=box.ROUNDED, 
            title_style=COGNICLI_ACCENT
        )
        table.add_column("Task", style=COGNICLI_ACCENT)
        table.add_column("Metric", style="magenta")
        table.add_column("Value", style="green")
        
        for task, data in results["results"].items():
            for metric, value in data.items():
                if isinstance(value, (int, float)):
                    val = f"{value:.4f}" if isinstance(value, float) else str(value)
                    table.add_row(task, metric, val)
        
        self.console.print(table)
        
        # Show summary if available
        if "versions" in results:
            self.console.print(f"\n[dim]Evaluation completed with lm-eval version: {results['versions'].get('lm-eval', 'Unknown')}[/dim]")

    def start_interactive_chat(self):
        """Start interactive chat mode with enhanced features"""
        config = self.model_manager.get_current_config()
        if not config:
            self.console.print("[red]No model configuration found.[/red]")
            return
        
        # Show chat header
        self.console.print(Panel(
            f"[bold green]Chat Mode Active[/bold green]\n"
            f"Model: [bold]{config.name}[/bold]\n"
            f"Type: [cyan]{config.model_type.title()}[/cyan]\n"
            f"Precision: [yellow]{config.precision}[/yellow]\n"
            f"Temperature: [magenta]{config.temperature}[/magenta]\n"
            f"Max Tokens: [blue]{config.max_tokens}[/blue]",
            title="🚀 CogniCLI Chat",
            border_style=COGNICLI_ACCENT
        ))
        
        self.console.print(f"\n[dim]Type your messages below. Commands:[/dim]")
        self.console.print(f"[dim]  • [green]help[/green] - Show available commands[/dim]")
        self.console.print(f"[dim]  • [green]config[/green] - Show current configuration[/dim]")
        self.console.print(f"[dim]  • [green]benchmark[/green] - Run quick benchmark[/dim]")
        self.console.print(f"[dim]  • [green]clear[/green] - Clear chat history[/dim]")
        self.console.print(f"[dim]  • [green]exit[/green] or [green]quit[/green] - End chat[/dim]")
        self.console.print()
        
        chat_history = []
        
        while True:
            try:
                # Get user input with enhanced prompt
                prompt = Prompt.ask(
                    f"[bold {COGNICLI_ACCENT}]cognicli[/bold {COGNICLI_ACCENT}] [dim]>[/dim]",
                    default="",
                    show_default=False
                )
                
                if not prompt.strip():
                    continue
                    
                # Handle special commands
                if prompt.lower() in ["exit", "quit", "q"]:
                    self.console.print(f"\n[bold yellow]Goodbye from CogniCLI![/bold yellow] 🎉")
                    break
                    
                elif prompt.lower() in ["help", "?"]:
                    self.show_chat_help()
                    continue
                    
                elif prompt.lower() == "config":
                    self.show_current_config()
                    continue
                    
                elif prompt.lower() == "benchmark":
                    self.console.print(f"[{COGNICLI_ACCENT}]Running quick benchmark...[/{COGNICLI_ACCENT}]")
                    self.benchmark_model()
                    continue
                    
                elif prompt.lower() == "clear":
                    chat_history.clear()
                    self.console.print("[green]Chat history cleared.[/green]")
                    continue
                    
                elif prompt.lower() == "status":
                    self.show_model_status()
                    continue
                
                # Generate response
                self.console.print(f"\n[dim]🤖 Generating response...[/dim]")
                
                start_time = time.time()
                response = self.generate_response(prompt, stream=True, show_thinking=True)
                end_time = time.time()
                
                if response:
                    # Add to chat history
                    chat_history.append({
                        "user": prompt,
                        "assistant": response,
                        "timestamp": datetime.now(),
                        "response_time": end_time - start_time
                    })
                    
                    # Show response stats
                    response_time = end_time - start_time
                    self.console.print(f"\n[dim]⏱️  Response time: {response_time:.2f}s[/dim]")
                    
                self.console.print()  # Add spacing between exchanges
                
            except KeyboardInterrupt:
                self.console.print(f"\n[bold yellow]Chat interrupted. Type 'exit' to quit.[/bold yellow]")
            except Exception as e:
                self.console.print(f"[red]❌ Error: {e}[/red]")
                if self.console.is_interactive:
                    self.console.print(f"[dim]Type 'help' for available commands.[/dim]")

    def show_chat_help(self):
        """Show help for chat mode"""
        help_text = f"""
[bold {COGNICLI_ACCENT}]Chat Mode Commands:[/bold {COGNICLI_ACCENT}]

[green]help[/green]          - Show this help message
[green]config[/green]        - Show current model configuration
[green]benchmark[/green]     - Run quick performance benchmark
[green]status[/green]        - Show model and system status
[green]clear[/green]         - Clear chat history
[green]exit[/green]          - Exit chat mode

[bold {COGNICLI_ACCENT}]Model Information:[/bold {COGNICLI_ACCENT}]
• Just type your message to chat with the AI
• The model will respond based on your input
• Tool calls are automatically detected and executed
• Use Ctrl+C to interrupt long responses
"""
        self.console.print(Panel(help_text, title="📚 Chat Help", border_style=COGNICLI_ACCENT))

    def show_current_config(self):
        """Show current model configuration"""
        config = self.model_manager.get_current_config()
        if not config:
            self.console.print("[red]No model configuration found.[/red]")
            return
            
        config_text = f"""
[bold]Model Configuration:[/bold]

[cyan]Name:[/cyan] {config.name}
[cyan]Type:[/cyan] {config.model_type.title()}
[cyan]Precision:[/cyan] {config.precision}
[cyan]Context Length:[/cyan] {config.context_length:,}
[cyan]Temperature:[/cyan] {config.temperature}
[cyan]Top-p:[/cyan] {config.top_p}
[cyan]Max Tokens:[/cyan] {config.max_tokens}
[cyan]Device:[/cyan] {config.device}
[cyan]Trust Remote Code:[/cyan] {config.trust_remote_code}
[cyan]Use Fast Tokenizer:[/cyan] {config.use_fast_tokenizer}
[cyan]Created:[/cyan] {config.created_at.strftime('%Y-%m-%d %H:%M:%S')}
[cyan]Last Used:[/cyan] {config.last_used.strftime('%Y-%m-%d %H:%M:%S') if config.last_used else 'Never'}
"""
        self.console.print(Panel(config_text, title="⚙️ Configuration", border_style=COGNICLI_ACCENT))

    def show_model_status(self):
        """Show current model and system status"""
        config = self.model_manager.get_current_config()
        
        # System info
        system_info = f"""
[bold]System Status:[/bold]

[cyan]Python Version:[/cyan] {sys.version.split()[0]}
[cyan]PyTorch Version:[/cyan] {torch.__version__}
[cyan]CUDA Available:[/cyan] {'Yes' if torch.cuda.is_available() else 'No'}
[cyan]GPU Count:[/cyan] {torch.cuda.device_count() if torch.cuda.is_available() else 0}
[cyan]Memory Usage:[/cyan] {psutil.virtual_memory().percent}%
[cyan]CPU Usage:[/cyan] {psutil.cpu_percent()}%
"""
        
        if config:
            model_info = f"""
[bold]Model Status:[/bold]

[cyan]Model:[/cyan] {config.name}
[cyan]Type:[/cyan] {config.model_type.title()}
[cyan]Status:[/cyan] [green]Loaded and Ready[/green]
[cyan]Device:[/cyan] {self.model_manager.current_model.device if hasattr(self.model_manager.current_model, 'device') else 'Unknown'}
"""
            system_info += model_info
        else:
            system_info += "\n[bold]Model Status:[/bold]\n\n[red]No model loaded[/red]"
        
        self.console.print(Panel(system_info, title="📊 System Status", border_style=COGNICLI_ACCENT))

    def show_welcome_message(self, model_loaded: bool):
        """Show welcome message with helpful information"""
        welcome_text = f"""
[bold {COGNICLI_ACCENT}]Welcome to CogniCLI v2.0.8 - Premium Edition![/bold {COGNICLI_ACCENT}] 🎉

[dim]🚀 Enhanced Features:[/dim]
• [green]Robust Model Loading[/green] - Better error handling and recovery
• [green]Premium UI[/green] - Beautiful tables, panels, and progress indicators
• [green]Advanced Benchmarking[/green] - Comprehensive performance metrics
• [green]Enhanced Chat Mode[/green] - Interactive chat with command support
• [green]Better Error Handling[/green] - Graceful failures and recovery

[dim]🔧 Quick Commands:[/dim]
• [green]--model <id>[/green]            Load a Hugging Face model
• [green]--list [filter][/green]         Browse available models
• [green]--search <query>[/green]        Search for models on Hugging Face
• [green]--info <id>[/green]             Show detailed model information
• [green]--files <id>[/green]            Browse model files and GGUF variants
• [green]--benchmark[/green]             Run performance benchmark
• [green]--lm_eval <tag|task|all>[/green] Run lm-eval-harness
• [green]--chat[/green]                  Start interactive chat mode after loading a model

[dim]🦙 Ollama Integration:[/dim]
• [green]--ollama list[/green]           List available Ollama models
• [green]--ollama search <query>[/green] Search Ollama models
• [green]--ollama pull <model>[/green]   Pull model from Ollama
• [green]--ollama quantizations[/green]  Show quantization options

[dim]🧠 Model Support:[/dim]
• [cyan]Transformers[/cyan] - Native PyTorch models with GPU acceleration
• [cyan]GGUF[/cyan] - Optimized quantized models via llama.cpp
• [cyan]Synapse[/cyan] - Specialized reasoning models with <think>/<answer> tags
• [cyan]Quantization[/cyan] - 4-bit and 8-bit support via BitsAndBytes

[dim]🎯 Precision Options:[/dim]
• [yellow]--type bf16[/yellow] - BFloat16 for optimal performance
• [yellow]--type fp16[/yellow] - Half precision for memory efficiency
• [yellow]--type q4[/yellow] - 4-bit quantization (memory efficient)
• [yellow]--type q8[/yellow] - 8-bit quantization (balanced)
"""
        
        self.console.print(Panel(welcome_text, title="🌟 CogniCLI Premium", border_style=COGNICLI_ACCENT))
        
        if not model_loaded:
            self.console.print(
                f"\n[bold yellow]No model loaded.[/bold yellow] To get started:\n"
                f"• Type [{COGNICLI_ACCENT}]--model <model_id>[/{COGNICLI_ACCENT}] to load a model\n"
                f"• Type [{COGNICLI_ACCENT}]--list[/{COGNICLI_ACCENT}] to browse available models\n"
                f"• Type [{COGNICLI_ACCENT}]--chat[/{COGNICLI_ACCENT}] to start interactive mode\n"
            )
        else:
            self.console.print(
                f"\n[bold green]Model loaded and ready![/bold green]\n"
                f"• Type [{COGNICLI_ACCENT}]--chat[/{COGNICLI_ACCENT}] to start chatting\n"
                f"• Type [{COGNICLI_ACCENT}]--benchmark[/{COGNICLI_ACCENT}] to test performance\n"
                f"• Type [{COGNICLI_ACCENT}]--lm_eval[/{COGNICLI_ACCENT}] to run evaluations\n"
            )
        
        self.console.print(f"\n[dim]Type [green]help[/green] for commands or [red]exit[/red] to quit.[/dim]\n")

    def start_interactive_mode(self, model_loaded: bool):
        """Start interactive mode with custom prompt - shows logo first, then custom prompt"""
        if model_loaded:
            config = self.model_manager.get_current_config()
            if config:
                self.console.print(f"[dim]Model loaded: {config.name} ({config.model_type.title()})[/dim]")
        
        # Removed duplicate message
        
        chat_history = []
        
        while True:
            try:
                # Get user input with custom prompt
                prompt = Prompt.ask(
                    f"[bold {COGNICLI_ACCENT}]cognicli[/bold {COGNICLI_ACCENT}] [dim]>[/dim]",
                    default="",
                    show_default=False
                )
                
                if not prompt.strip():
                    continue
                    
                # Handle special commands
                if prompt.lower() in ["exit", "quit", "q"]:
                    self.console.print(f"\n[bold yellow]Goodbye from CogniCLI![/bold yellow] 🎉")
                    break
                    
                elif prompt.lower() in ["help", "?"]:
                    self.show_interactive_help()
                    continue
                    
                elif prompt.lower() == "config":
                    self.show_current_config()
                    continue
                    
                elif prompt.lower() == "benchmark":
                    if not model_loaded:
                        self.console.print(f"[red]No model loaded. Use 'load <model_id>' or --model to load a model first.[/red]")
                        continue
                    self.console.print(f"[{COGNICLI_ACCENT}]Running quick benchmark...[/{COGNICLI_ACCENT}]")
                    self.benchmark_model()
                    continue
                    
                elif prompt.lower() == "clear":
                    chat_history.clear()
                    self.console.print("[green]Chat history cleared.[/green]")
                    continue
                    
                elif prompt.lower() == "status":
                    self.show_model_status()
                    continue
                
                elif prompt.lower() == "load":
                    self._handle_load_command()
                    continue
                
                elif prompt.lower() == "list":
                    self._handle_list_command()
                    continue
                
                # Check if this is a command-line style argument
                if prompt.startswith('--'):
                    self._handle_cli_argument(prompt, model_loaded)
                    continue
                
                # Generate response if model is loaded
                if not model_loaded:
                    self.console.print(f"[red]No model loaded. Use 'load <model_id>' or --model to load a model first.[/red]")
                    continue
                
                # Generate response
                self.console.print(f"\n[dim]🤖 Generating response...[/dim]")
                
                start_time = time.time()
                response = self.generate_response(prompt, stream=True, show_thinking=True)
                end_time = time.time()
                
                if response:
                    # Add to chat history
                    chat_history.append({
                        "user": prompt,
                        "assistant": response,
                        "timestamp": datetime.now(),
                        "response_time": end_time - start_time
                    })
                    
                    # Show response stats
                    response_time = end_time - start_time
                    self.console.print(f"\n[dim]⏱️  Response time: {response_time:.2f}s[/dim]")
                    
                self.console.print()  # Add spacing between exchanges
                
            except KeyboardInterrupt:
                self.console.print(f"\n[bold yellow]Interactive mode interrupted. Type 'exit' to quit.[/bold yellow]")
            except Exception as e:
                self.console.print(f"[red]❌ Error: {e}[/red]")
                if self.console.is_interactive:
                    self.console.print(f"[dim]Type 'help' for available commands.[/dim]")

    def show_interactive_help(self):
        """Show help for interactive mode"""
        help_text = f"""
[bold {COGNICLI_ACCENT}]Interactive Mode Commands:[/bold {COGNICLI_ACCENT}]

[green]help[/green]          - Show this help message
[green]config[/green]        - Show current model configuration
[green]benchmark[/green]     - Run quick performance benchmark
[green]status[/green]        - Show model and system status
[green]clear[/green]         - Clear chat history
[green]load <model>[/green]  - Load a model (e.g., 'load gpt2')
[green]list[/green]          - List available models
[green]exit[/green]          - Exit interactive mode

[bold {COGNICLI_ACCENT}]Command-Line Style Arguments:[/bold {COGNICLI_ACCENT}]
[green]--model <id>[/green]            Load a Hugging Face model
[green]--list [filter][/green]         Browse available models
[green]--search <query>[/green]        Search for models on Hugging Face
[green]--info <id>[/green]             Show detailed model information
[green]--files <id>[/green]            Browse model files and GGUF variants
[green]--benchmark[/green]             Run performance benchmark
[green]--chat[/green]                  Start interactive chat mode after loading a model
[green]--generate <text>[/green]       Generate response for text
[green]--ollama list[/green]           List available Ollama models
[green]--ollama search <query>[/green] Search Ollama models
[green]--ollama pull <model>[/green]   Pull model from Ollama
[green]--ollama quantizations[/green]  Show quantization options
[green]--help[/green]                  Show this help message

[bold {COGNICLI_ACCENT}]Model Information:[/bold {COGNICLI_ACCENT}]
• Just type your message to chat with the AI
• The model will respond based on your input
• Tool calls are automatically detected and executed
• Use Ctrl+C to interrupt long responses
• Use command-line style arguments for model management
"""
        self.console.print(Panel(help_text, title="📚 Interactive Help", border_style=COGNICLI_ACCENT))

    def _handle_load_command(self):
        """Handle the load command in interactive mode"""
        model_id = Prompt.ask(
            f"[bold {COGNICLI_ACCENT}]Enter model ID[/bold {COGNICLI_ACCENT}] [dim](e.g., gpt2)[/dim]",
            default="",
            show_default=False
        )
        
        if not model_id.strip():
            self.console.print("[yellow]No model ID provided.[/yellow]")
            return
        
        # Load the model
        success = self.load_model(model_id.strip())
        if success:
            self.console.print(f"[bold green]✅ Model {model_id} loaded successfully![/bold green]")
            # Update the model_loaded state for the caller
            return True
        else:
            self.console.print(f"[red]❌ Failed to load model {model_id}[/red]")
            return False

    def _handle_list_command(self):
        """Handle the list command in interactive mode"""
        filter_term = Prompt.ask(
            f"[bold {COGNICLI_ACCENT}]Enter filter term[/bold {COGNICLI_ACCENT}] [dim](optional, e.g., llama)[/dim]",
            default="",
            show_default=False
        )
        
        models = self.list_models(filter_term.strip())
        if models:
            table = Table(
                title="Available Models", 
                box=box.ROUNDED, 
                title_style=COGNICLI_ACCENT
            )
            table.add_column("Model ID", style=COGNICLI_ACCENT, no_wrap=True)
            table.add_column("Downloads", style="green", justify="right")
            table.add_column("Likes", style="yellow", justify="right")
            table.add_column("Tags", style="blue")
            
            for model in models[:10]:  # Show top 10 models
                tags = ", ".join(model['tags'][:2]) if model['tags'] else "N/A"
                table.add_row(
                    model['id'], 
                    f"{model['downloads']:,}", 
                    f"{model['likes']:,}", 
                    tags
                )
            self.console.print(table)
        else:
                         self.console.print("[yellow]No models found.[/yellow]")

    def _handle_cli_argument(self, prompt: str, model_loaded: bool):
        """Handle command-line style arguments within interactive mode"""
        try:
            # Parse the argument string
            args = prompt.split()
            
            if args[0] == '--model' and len(args) > 1:
                model_id = args[1]
                self.console.print(f"[{COGNICLI_ACCENT}]Loading model: {model_id}[/{COGNICLI_ACCENT}]")
                
                # Parse additional arguments
                kwargs = {}
                i = 2
                while i < len(args):
                    if args[i] == '--type' and i + 1 < len(args):
                        kwargs['precision'] = args[i + 1]
                        i += 2
                    elif args[i] == '--context' and i + 1 < len(args):
                        kwargs['context_length'] = int(args[i + 1])
                        i += 2
                    elif args[i] == '--temperature' and i + 1 < len(args):
                        kwargs['temperature'] = float(args[i + 1])
                        i += 2
                    elif args[i] == '--max-tokens' and i + 1 < len(args):
                        kwargs['max_tokens'] = int(args[i + 1])
                        i += 2
                    elif args[i] == '--top-p' and i + 1 < len(args):
                        kwargs['top_p'] = float(args[i + 1])
                        i += 2
                    else:
                        i += 1
                
                success = self.load_model(model_id, **kwargs)
                if success:
                    self.console.print(f"[bold green]✅ Model {model_id} loaded successfully![/bold green]")
                    # Update the model_loaded state for the caller
                    return True
                else:
                    self.console.print(f"[red]❌ Failed to load model {model_id}[/red]")
                    return False
                    
            elif args[0] == '--list':
                filter_term = args[1] if len(args) > 1 else ""
                self.console.print(f"[{COGNICLI_ACCENT}]Searching models...[/{COGNICLI_ACCENT}]")
                models = self.list_models(filter_term)
                
                if models:
                    table = Table(
                        title="Available Models", 
                        box=box.ROUNDED, 
                        title_style=COGNICLI_ACCENT
                    )
                    table.add_column("Model ID", style=COGNICLI_ACCENT, no_wrap=True)
                    table.add_column("Downloads", style="green", justify="right")
                    table.add_column("Likes", style="yellow", justify="right")
                    table.add_column("Tags", style="blue")
                    
                    for model in models[:10]:  # Show top 10 models
                        tags = ", ".join(model['tags'][:2]) if model['tags'] else "N/A"
                        table.add_row(
                            model['id'], 
                            f"{model['downloads']:,}", 
                            f"{model['likes']:,}", 
                            tags
                        )
                    self.console.print(table)
                else:
                    self.console.print("[yellow]No models found.[/yellow]")
                    
            elif args[0] == '--info' and len(args) > 1:
                model_id = args[1]
                self.show_model_info(model_id)
                
            elif args[0] == '--files' and len(args) > 1:
                model_id = args[1]
                self.show_model_files(model_id)
                
            elif args[0] == '--benchmark':
                if not model_loaded:
                    self.console.print(f"[red]No model loaded. Use --model to load a model first.[/red]")
                    return
                self.console.print(f"[{COGNICLI_ACCENT}]Running benchmark...[/{COGNICLI_ACCENT}]")
                self.benchmark_model()
                
            elif args[0] == '--chat':
                if not model_loaded:
                    self.console.print(f"[red]No model loaded. Use --model to load a model first.[/red]")
                    return
                self.start_interactive_chat()
                
            elif args[0] == '--generate' and len(args) > 1:
                if not model_loaded:
                    self.console.print(f"[red]No model loaded. Use --model to load a model first.[/red]")
                    return
                text = " ".join(args[1:])
                self.console.print(f"[{COGNICLI_ACCENT}]Generating response for: {text}[/{COGNICLI_ACCENT}]")
                self.generate_response(text, stream=True, show_thinking=True)
                
            elif args[0] == '--help':
                self.show_interactive_help()
                
            elif args[0] == '--ollama' and len(args) > 1:
                if args[1] == 'list':
                    cli.handle_ollama_operations("list")
                elif args[1] == 'search':
                    cli.handle_ollama_operations("search", args[2])
                elif args[1] == 'pull':
                    cli.handle_ollama_operations("pull", args[2])
                elif args[1] == 'quantizations':
                    cli.handle_ollama_operations("quantizations")
                else:
                    cli.console.print(f"[red]Invalid Ollama operation: {args[1]}[/red]")
                    cli.console.print(f"[dim]Valid operations: list, search <query>, pull <model>[:<quantization>], quantizations[/dim]")
                
            else:
                self.console.print(f"[yellow]Unknown argument: {args[0]}[/yellow]")
                self.console.print(f"[dim]Type 'help' for available commands.[/dim]")
                
        except Exception as e:
            self.console.print(f"[red]Error processing argument: {e}[/red]")
 

# Benchmark presets
ALL_BENCHMARK_TASKS = [
    "hellaswag", "arc_easy", "arc_challenge", "winogrande", "mmlu",
    "gsm8k", "wikitext", "openbookqa", "piqa", "lambada", "mathqa", "boolq"
]

BENCHMARK_PRESETS = {
    "reasoning": ["hellaswag", "arc_easy", "arc_challenge", "winogrande", "piqa", "gsm8k", "mmlu"],
    "math": ["gsm8k", "mathqa"],
    "reading": ["wikitext", "lambada", "boolq"],
    "all": ALL_BENCHMARK_TASKS
}

if __name__ == "__main__":
    main()
