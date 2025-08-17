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
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

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

class AnimatedSpinner:
    def __init__(self, text: str):
        self.text = text
        self.spinning = False
        self.thread = None
    def start(self):
        self.spinning = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()
    def stop(self):
        self.spinning = False
        if self.thread:
            self.thread.join()
    def _spin(self):
        spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        i = 0
        while self.spinning:
            char = spinner_chars[i % len(spinner_chars)]
            sys.stdout.write(f'\r{Fore.MAGENTA}{char} {self.text}{Style.RESET_ALL}')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

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


class CogniCLI:
    def __init__(self):
        self.console = Console()
        self.models: Dict[str, ModelConfig] = {}
        self.current_model = None
        self.current_tokenizer = None
        self.api = HfApi()
        self.cache_dir = Path.home() / '.cognicli'
        self.cache_dir.mkdir(exist_ok=True)
        self.system_tool_prompt = SYSTEM_TOOL_PROMPT.strip()
        self.synapse_system_prompt = self._get_synapse_system_prompt()

    def show_logo(self):
        from rich.align import Align
        logo_text = Text(LOGO)
        logo_text.stylize(f"bold {COGNICLI_ACCENT}")
        panel = Panel(
            logo_text,
            border_style=COGNICLI_ACCENT,
            title="CogniCLI",
            subtitle="Premium AI Command Line",
            padding=(1, 4),
        )
        # Center the panel itself (not just the text)
        self.console.print(Align.center(panel))

    def list_models(self, filter_term: str = "") -> List[dict]:
        models = self.api.list_models(filter="text-generation")
        out = []
        for model in models:
            if filter_term.lower() in model.modelId.lower():
                info = {
                    "id": model.modelId,
                    "downloads": getattr(model, "downloads", 0),
                    "likes": getattr(model, "likes", 0),
                    "tags": getattr(model, "tags", []),
                }
                out.append(info)
        return sorted(out, key=lambda x: x['downloads'], reverse=True)

    def show_model_info(self, model_id: str):
        try:
            info = self.api.model_info(model_id)
            panel = Panel(
                f"[bold]{info.modelId}[/bold]\n"
                f"[{COGNICLI_ACCENT}]Likes:[/] {info.likes}\n"
                f"[{COGNICLI_ACCENT}]Downloads:[/] {info.downloads}\n"
                f"[{COGNICLI_ACCENT}]Tags:[/] {', '.join(info.tags)}\n"
                f"[{COGNICLI_ACCENT}]Card:[/]\n{info.cardData.get('summary', 'No summary.')}\n",
                title=model_id,
                border_style=COGNICLI_ACCENT,
            )
            self.console.print(panel)
        except Exception as e:
            self.console.print(f"[red]Failed to get info for model: {e}[/red]")

    def show_model_files(self, model_id: str):
        try:
            files = self.api.list_files(model_id)
            table = Table(title=f"Files for {model_id}", box=box.ROUNDED, title_style=COGNICLI_ACCENT)
            table.add_column("File Name", style=COGNICLI_ACCENT)
            table.add_column("Size", style="green")
            table.add_column("SHA256", style="yellow")
            for f in files:
                table.add_row(f.rfilename, self._format_size(f.size), f.sha256[:8])
            self.console.print(table)
        except Exception as e:
            self.console.print(f"[red]Failed to get files for model: {e}[/red]")

    def _is_synapse_model(self, model_id: str) -> bool:
        """Check if a model is a Synapse model by examining its config"""
        try:
            config_info = self.api.model_info(model_id)
            # Check if config.json contains synapse-specific fields
            for file_info in config_info.siblings:
                if file_info.rfilename == "config.json":
                    # Download and check config
                    config_path = hf_hub_download(repo_id=model_id, filename="config.json")
                    with open(config_path, 'r') as f:
                        config = json.load(f)

                    # Check for Synapse-specific indicators
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
        except Exception as e:
            # If we can't determine, assume it's not a Synapse model
            pass
        return False

    def _get_synapse_system_prompt(self) -> str:
        """Get the appropriate system prompt for Synapse models"""
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
{"tool_call": "python_eval", "args": {"code": "print(2 + 2)"}}
"""

    def load_model(self, model_id, model_type="auto", precision="auto", gguf_file=None, context_length=2048) -> bool:
        spinner = AnimatedSpinner(f"Loading {model_id} ...")
        spinner.start()
        try:
            # GGUF
            if gguf_file or model_type == "gguf":
                gguf_path = gguf_file or self._download_gguf_model(model_id)
                from llama_cpp import Llama
                self.current_model = Llama(model_path=str(gguf_path), n_ctx=context_length)
                config = ModelConfig(
                    name=model_id,
                    model_type="gguf",
                    precision=precision,
                    context_length=context_length,
                    temperature=0.7,
                    top_p=0.95,
                    max_tokens=512,
                )
                self.models[model_id] = config
                spinner.stop()
                self.console.print(f"[bold green]Loaded GGUF model:[/] {model_id}")
                return True
            # Transformers (including Synapse models)
            else:
                quant_config = self._get_quantization_config(precision)

                # Check if this is a Synapse model by looking at config
                is_synapse_model = self._is_synapse_model(model_id)

                if is_synapse_model:
                    self.console.print(f"[{COGNICLI_ACCENT}]Detected Synapse model - loading with custom architecture[/]")

                model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    device_map="auto",
                    trust_remote_code=True,
                    **quant_config
                )
                tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)

                # Add special tokens for Synapse models
                if is_synapse_model:
                    special_tokens = ['<think>', '</think>', '<answer>', '</answer>']
                    tokenizer.add_special_tokens({'additional_special_tokens': special_tokens})
                    # Resize embeddings if needed
                    if hasattr(model, 'resize_token_embeddings'):
                        model.resize_token_embeddings(len(tokenizer))

                self.current_model = model
                self.current_tokenizer = tokenizer
                config = ModelConfig(
                    name=model_id,
                    model_type="synapse" if is_synapse_model else "transformers",
                    precision=precision,
                    context_length=context_length,
                    temperature=0.7,
                    top_p=0.95,
                    max_tokens=512,
                )
                self.models[model_id] = config
                spinner.stop()
                model_type_display = "Synapse" if is_synapse_model else "Transformers"
                self.console.print(f"[bold green]Loaded {model_type_display} model:[/] {model_id}")
                return True
        except Exception as e:
            spinner.stop()
            self.console.print(f"[red]Failed to load model: {e}[/red]")
            return False

    def _download_gguf_model(self, model_id) -> Path:
        # Try to find a .gguf file in the repo
        files = self.api.list_files(model_id)
        gguf_file = next((f for f in files if f.rfilename.endswith(".gguf")), None)
        if not gguf_file:
            raise RuntimeError(f"No GGUF file found for {model_id}")
        path = self.cache_dir / gguf_file.rfilename
        if not path.exists():
            self.console.print(f"[yellow]Downloading GGUF file: {gguf_file.rfilename} ...[/yellow]")
            hf_hub_download(repo_id=model_id, filename=gguf_file.rfilename, local_dir=self.cache_dir)
        return path

    def _format_size(self, nbytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if nbytes < 1024:
                return f"{nbytes:.1f} {unit}"
            nbytes /= 1024
        return f"{nbytes:.1f} TB"

    def _get_file_type(self, fname: str) -> str:
        if fname.endswith(".gguf"):
            return "gguf"
        return "unknown"

    def _get_torch_dtype(self, precision: str):
        if precision == "fp16":
            return torch.float16
        elif precision == "bf16":
            return torch.bfloat16
        elif precision == "fp32":
            return torch.float32
        else:
            return torch.float32

    def _get_quantization_config(self, precision: str):
        # Use bitsandbytes if available for q4/q8
        if precision in ("q4", "q8") and BNB_AVAILABLE:
            load_in_8bit = (precision == "q8")
            load_in_4bit = (precision == "q4")
            return {"load_in_8bit": load_in_8bit, "load_in_4bit": load_in_4bit}
        elif precision in ("fp16", "bf16"):
            return {"torch_dtype": self._get_torch_dtype(precision)}
        return {}

    def _generate_synapse(self, prompt: str, config: ModelConfig) -> str:
        """Generate response specifically for Synapse models with proper formatting"""
        if not self.current_model or not self.current_tokenizer:
            self.console.print("[red]No Synapse model loaded.[/red]")
            return ""

        # Use Synapse-specific system prompt
        system_prompt = self._get_synapse_system_prompt()
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"

        # Tokenize and generate
        inputs = self.current_tokenizer(full_prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to(self.current_model.device)
        attention_mask = inputs.get("attention_mask", None)

        gen_args = {
            "input_ids": input_ids,
            "max_new_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "do_sample": True,
            "eos_token_id": self.current_tokenizer.eos_token_id,
            "pad_token_id": self.current_tokenizer.eos_token_id,
            "repetition_penalty": 1.1,
        }

        if attention_mask is not None:
            gen_args["attention_mask"] = attention_mask.to(self.current_model.device)

        with torch.no_grad():
            outputs = self.current_model.generate(**gen_args)

        # Decode only the new tokens
        response = self.current_tokenizer.decode(
            outputs[0][input_ids.shape[1]:],
            skip_special_tokens=True
        )

        return response

    def _generate_gguf(self, prompt, stream, show_thinking, config: ModelConfig) -> str:
        # Only for GGUF models loaded via llama-cpp-python
        if not self.current_model:
            self.console.print("[red]No GGUF model loaded.[/red]")
            return ""
        response = self.current_model(prompt=prompt, max_tokens=config.max_tokens, temperature=config.temperature)
        return response['choices'][0]['text']

    def _generate_transformers(self, prompt, stream, show_thinking, config: ModelConfig) -> str:
        if not self.current_model or not self.current_tokenizer:
            self.console.print("[red]No Transformers model loaded.[/red]")
            return ""
        inputs = self.current_tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to(self.current_model.device)
        attention_mask = inputs.get("attention_mask", None)
        gen_args = {
            "input_ids": input_ids,
            "max_new_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "do_sample": True,
        }
        if attention_mask is not None:
            gen_args["attention_mask"] = attention_mask.to(self.current_model.device)
        with torch.no_grad():
            outputs = self.current_model.generate(**gen_args)
        out = self.current_tokenizer.decode(outputs[0][input_ids.shape[1]:], skip_special_tokens=True)
        return out

    def generate_response(self, prompt: str, stream: bool = True, show_thinking: bool = True) -> str:
        if not self.current_model:
            self.console.print(f"[{COGNICLI_ACCENT}]No model loaded. Use --model to load a model.[/{COGNICLI_ACCENT}]")
            return ""

        config = list(self.models.values())[-1]

        # Handle different model types
        if config.model_type == "gguf":
            full_prompt = self.system_tool_prompt + "\n\nUser: " + prompt
            response = self._generate_gguf(full_prompt, stream, show_thinking, config)
        elif config.model_type == "synapse":
            response = self._generate_synapse(prompt, config)
        else:
            full_prompt = self.system_tool_prompt + "\n\nUser: " + prompt
            response = self._generate_transformers(full_prompt, stream, show_thinking, config)

        # Handle tool calls
        tool_call = extract_tool_call(response)
        if tool_call:
            process_tool_call(tool_call, self.console)
        else:
            # For Synapse models, handle the thinking display specially
            if config.model_type == "synapse" and show_thinking:
                self._display_synapse_response(response)
            else:
                self.console.print(Markdown(response) if response else "")

        return response

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

    def benchmark_model(self):
        # Simple benchmark: generate 32 tokens 5 times and time it
        if not self.current_model:
            self.console.print("[red]No model loaded.[/red]")
            return {}
        prompt = "The quick brown fox jumps over the lazy dog."
        results = []
        for _ in range(5):
            start = time.time()
            if hasattr(self.current_model, "__call__"):
                _ = self.current_model(prompt=prompt, max_tokens=32)
            else:
                input_ids = self.current_tokenizer(prompt, return_tensors="pt")["input_ids"].to(self.current_model.device)
                _ = self.current_model.generate(input_ids=input_ids, max_new_tokens=32)
            end = time.time()
            results.append(end - start)
        mean = np.mean(results)
        std = np.std(results)
        table = Table(title="Benchmark Results", box=box.ROUNDED, title_style=COGNICLI_ACCENT)
        table.add_column("Mean (s)", style=COGNICLI_ACCENT)
        table.add_column("Std (s)", style="magenta")
        table.add_column("Runs", style="green")
        table.add_row(f"{mean:.3f}", f"{std:.3f}", f"{len(results)}")
        self.console.print(table)
        return {"mean": mean, "std": std, "runs": len(results)}

    def run_lm_eval(self, tasks="hellaswag", num_fewshot=0):
        self.console.print(f"[{COGNICLI_ACCENT}]Running lm-eval-harness...[/]")
        try:
            import lm_eval
            from lm_eval import evaluator
        except ImportError:
            self.console.print(f"[{COGNICLI_ACCENT}]lm-eval-harness not installed. Installing...[/]")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'lm-eval'])
            import lm_eval
            from lm_eval import evaluator
        model_args = {
            "pretrained": list(self.models.keys())[-1],
            "revision": "main",
            "trust_remote_code": True,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
        }
        results = evaluator.simple_evaluate(
            model="hf-causal-experimental",
            model_args=",".join(f"{k}={v}" for k, v in model_args.items()),
            tasks=tasks,
            num_fewshot=num_fewshot,
            batch_size=1,
        )
        table = Table(title="LM Evaluation Results", box=box.ROUNDED, title_style=COGNICLI_ACCENT)
        table.add_column("Task", style=COGNICLI_ACCENT)
        table.add_column("Metric", style="magenta")
        table.add_column("Value", style="green")
        for task, data in results["results"].items():
            for metric, value in data.items():
                val = f"{value:.4f}" if isinstance(value, float) else str(value)
                table.add_row(task, metric, val)
        self.console.print(table)


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

def main():
    parser = argparse.ArgumentParser(description="CogniCLI - Premium AI Command Line Interface")
    parser.add_argument('--model', type=str, help='Model to load (Hugging Face model ID)')
    parser.add_argument('--type', choices=['bf16', 'fp16', 'fp32', 'q4', 'q8'], default='auto', help='Model precision')
    parser.add_argument('--gguf-file', type=str, help='Specific GGUF file to use')
    parser.add_argument('--context', type=int, default=2048, help='Context length')
    parser.add_argument('--no-think', action='store_true', help='Disable reasoning traces')
    parser.add_argument('--no-stream', action='store_true', help='Disable streaming output')
    parser.add_argument('--temperature', type=float, default=0.7, help='Sampling temperature')
    parser.add_argument('--max-tokens', type=int, default=512, help='Maximum tokens to generate')
    parser.add_argument('--chat', action='store_true', help='Start interactive chat mode')
    parser.add_argument('--generate', type=str, help='Generate response for prompt')
    parser.add_argument('--benchmark', action='store_true', help='Run model benchmark')
    parser.add_argument('--lm_eval', type=str, nargs='?', const="hellaswag", help='Run lm-eval-harness: e.g. --lm_eval mmlu or --lm_eval all')
    face_parser = parser.add_mutually_exclusive_group()
    face_parser.add_argument('--list', type=str, nargs='?', const='', help='List models (optional filter)')
    face_parser.add_argument('--info', type=str, help='Show detailed model info')
    face_parser.add_argument('--files', type=str, help='Show model files')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    parser.add_argument('--save-benchmark', type=str, help='Save benchmark results to file')
    args = parser.parse_args()

    cli = CogniCLI()
    cli.show_logo()

    if args.list is not None:
        models = cli.list_models(args.list)
        if args.json:
            print(json.dumps(models, indent=2))
        else:
            table = Table(title="Available Models", box=box.ROUNDED, title_style=COGNICLI_ACCENT)
            table.add_column("Model ID", style=COGNICLI_ACCENT, no_wrap=True)
            table.add_column("Downloads", style="green", justify="right")
            table.add_column("Likes", style="yellow", justify="right")
            table.add_column("Tags", style="blue")
            for model in models[:15]:
                tags = ", ".join(model['tags'][:3]) if model['tags'] else "N/A"
                table.add_row(model['id'], f"{model['downloads']:,}", f"{model['likes']:,}", tags)
            cli.console.print(table)
        return

    if args.info:
        cli.show_model_info(args.info)
        return

    if args.files:
        cli.show_model_files(args.files)
        return

    loaded_model = False
    if args.model:
        model_type = "gguf" if args.gguf_file else "auto"
        loaded_model = cli.load_model(
            args.model,
            model_type=model_type,
            precision=args.type,
            gguf_file=args.gguf_file,
            context_length=args.context
        )

    if args.benchmark:
        results = cli.benchmark_model()
        if args.json:
            print(json.dumps(results, indent=2))
        if args.save_benchmark:
            with open(args.save_benchmark, 'w') as f:
                json.dump(results, f, indent=2)
            cli.console.print(f"[green]Benchmark results saved to {args.save_benchmark}[/green]")
        return

    if args.generate:
        cli.generate_response(
            args.generate,
            stream=not args.no_stream,
            show_thinking=not args.no_think
        )
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

    cli.console.print(f"[bold {COGNICLI_ACCENT}]Welcome to CogniCLI![/bold {COGNICLI_ACCENT}] 🎉")
    cli.console.print(
        f"[yellow]Some helpful commands:[/yellow]\n"
        f"[{COGNICLI_ACCENT}]  --model <id>[/{COGNICLI_ACCENT}]            Load a Hugging Face model\n"
        f"[{COGNICLI_ACCENT}]  --lm_eval <tag|task|all>[/{COGNICLI_ACCENT}] Run lm-eval-harness (tags: [magenta]reasoning[/magenta], [magenta]math[/magenta], [magenta]reading[/magenta], [magenta]all[/magenta], or any single benchmark)\n"
        f"[{COGNICLI_ACCENT}]  help[/{COGNICLI_ACCENT}]                    Show help in the shell\n"
        f"[{COGNICLI_ACCENT}]  exit[/{COGNICLI_ACCENT}]                    Quit\n\n"
        f"[bold {COGNICLI_ACCENT}]🧠 Synapse Model Support:[/bold {COGNICLI_ACCENT}]\n"
        "- Automatic detection of Synapse models\n"
        "- Custom reasoning with <think>/<answer> tags\n"
        "- Optimized generation parameters\n\n"
        f"[bold {COGNICLI_ACCENT}]Tools enabled in chat:[/bold {COGNICLI_ACCENT}]\n"
        "- write_file, append_file, read_file, list_dir, run_shell, python_eval, pip_install\n"
        f"  e.g. [green]{{'tool_call': 'write_file', 'args': {{'filepath': 'a.py', 'content': 'print(123)'}}}}[/green]"
    )
    if not loaded_model:
        cli.console.print(
            f"[bold yellow]No model loaded.[/bold yellow] Type [{COGNICLI_ACCENT}]--model <model_id>[/{COGNICLI_ACCENT}] to load a model.\n"
            f"Or type [{COGNICLI_ACCENT}]list[/{COGNICLI_ACCENT}] to browse available models."
        )
    cli.console.print(f"Type [green]help[/green] for commands. Type [red]exit[/red] to quit.\n")

    while True:
        try:
            prompt = input("cognicli > ").strip()
            if prompt.lower() in ["exit", "quit"]:
                cli.console.print(f"\n[bold yellow]Goodbye from CogniCLI![/bold yellow]")
                break
            elif prompt.lower() in ["help", "?"]:
                cli.console.print(
                    f"[bold {COGNICLI_ACCENT}]Commands:[/bold {COGNICLI_ACCENT}]\n"
                    "  [green]help[/green]                Show this help\n"
                    "  [green]exit[/green]                Quit CogniCLI\n"
                    "  [green]list[/green]                List available models\n"
                    "  [green]--model <id>[/green]        Load a model (supports Synapse models!)\n"
                    "  [green]--files <id>[/green]        Show model files\n"
                    "  [green]--lm_eval <tag|task|all>[/green] Run lm-eval-harness\n"
                    "  [green]--benchmark[/green]         Run speed benchmark\n"
                    "  [green]--chat[/green]              Start chat mode\n"
                    "\n"
                    f"[bold {COGNICLI_ACCENT}]🧠 Synapse Features:[/bold {COGNICLI_ACCENT}]\n"
                    "  - Automatic detection and optimized loading\n"
                    "  - Beautiful reasoning display with <think>/<answer> tags\n"
                    "  - Custom system prompts for enhanced performance\n"
                    "\n"
                    f"[bold {COGNICLI_ACCENT}]Tool use (in chat, automatic):[/bold {COGNICLI_ACCENT}]\n"
                    "  write_file, append_file, read_file, list_dir, run_shell, python_eval, pip_install"
                )
            elif prompt.lower() == "list":
                models = cli.list_models()
                table = Table(title="Available Models", box=box.ROUNDED, title_style=COGNICLI_ACCENT)
                table.add_column("Model ID", style=COGNICLI_ACCENT, no_wrap=True)
                table.add_column("Downloads", style="green", justify="right")
                table.add_column("Likes", style="yellow", justify="right")
                table.add_column("Tags", style="blue")
                for model in models[:15]:
                    tags = ", ".join(model['tags'][:3]) if model['tags'] else "N/A"
                    table.add_row(model['id'], f"{model['downloads']:,}", f"{model['likes']:,}", tags)
                cli.console.print(table)
            elif prompt.startswith("--model"):
                parts = prompt.split()
                if len(parts) > 1:
                    loaded_model = cli.load_model(parts[1])
                else:
                    cli.console.print(f"[red]Please specify a model id after --model[/red]")
            elif prompt.startswith("--files"):
                parts = prompt.split()
                if len(parts) > 1:
                    cli.show_model_files(parts[1])
                else:
                    cli.console.print(f"[red]Please specify a model id after --files[/red]")
            elif prompt.startswith("--lm_eval"):
                parts = prompt.split()
                if len(parts) > 1:
                    tag = parts[1].strip().lower()
                else:
                    tag = "hellaswag"
                if not loaded_model:
                    cli.console.print(f"[red]No model loaded. Use --model to load a model first.[/red]")
                else:
                    if tag == "all":
                        tasks = ",".join(BENCHMARK_PRESETS["all"])
                    elif tag in BENCHMARK_PRESETS:
                        tasks = ",".join(BENCHMARK_PRESETS[tag])
                    else:
                        tasks = tag
                    cli.run_lm_eval(tasks=tasks)
            else:
                if not loaded_model:
                    cli.console.print(f"[red]No model loaded. Use --model to load a model first.[/red]")
                else:
                    cli.generate_response(prompt, stream=True, show_thinking=True)
        except KeyboardInterrupt:
            cli.console.print(f"\n[bold yellow]Goodbye from CogniCLI![/bold yellow]")
            break

if __name__ == "__main__":
    main()
