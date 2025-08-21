import json
import functools
from .database.model import Session, Project, Trace, Base, engine as default_engine, sessionmaker, TraceTypes
from sqlalchemy import create_engine
from datetime import datetime
from .connect import hora
from typing import Dict, Union
import pytz
import inspect
import threading
import subprocess
import os

class NovaTrace:
    def __init__(self, session_name: str, engine_url: str = None, time_zone: pytz.tzinfo = pytz.utc, interface: bool = True, interface_logs: bool = False):
        """
        Init a new NovaTrace instance.
        Args:
            session_name (str): Name of the session to be created or connected to.
            engine_url (str, optional): SQLAlchemy engine URL. If not provided, defaults to the default engine.
            time_zone (pytz.tzinfo, optional): Time zone for timestamps. Defaults to UTC.
            interface (bool, optional): Whether to start the Reflex web interface. Defaults to True.
            interface_logs (bool, optional): Whether to show detailed logs when interface is enabled. Defaults to False.
        Raises:
            ValueError: If metadata is not provided or incomplete.
        Returns:
            None
        """
        self.time_zone = time_zone
        self.interface_enabled = interface
        self.interface_logs = interface_logs
        self.reflex_process = None
        
        if engine_url:
            self.engine = create_engine(engine_url)
        else:
            self.engine = default_engine
        Base.metadata.create_all(self.engine)
        session = sessionmaker(bind=self.engine)

        self.session = session() # Sesion de SQLAlchemy

        for name in ["LLM", "Agent", "Tool"]:
            if not self.session.query(TraceTypes).filter_by(name=name).first():
                new_type = TraceTypes(name=name)
                self.session.add(new_type) 
        self.session.commit() # BDD Build

        self.active_session = self.session.query(Session).filter_by(name=session_name).first()

        if not self.active_session:
            self.active_session = Session(name=session_name, created_at=datetime.now(self.time_zone))
            self.session.add(self.active_session)
            self.session.commit()
        self.project = None
        self.provider: str = None
        self.model: str = None
        self.input_cost_per_million_tokens: float = 0.0
        self.output_cost_per_million_tokens: float = 0.0
        self.user_external_id: str = "guest_user"
        self.user_external_name: str = "Guest User"
        
        # Start Reflex interface if enabled
        if self.interface_enabled:
            self._start_reflex_interface()
    
    def _start_reflex_interface(self):
        """
        Start the Reflex web interface in a separate thread.
        This will start both frontend (port 3000) and backend (port 8000).
        """
        def run_reflex():
            try:
                # Change to the web_interface directory where rxconfig.py is located
                current_dir = os.path.dirname(os.path.abspath(__file__))
                web_interface_dir = os.path.join(current_dir, "web_interface")
                novatrace_root = os.path.dirname(current_dir)  # Parent directory of novatrace package
                
                # Check if web_interface directory exists
                if not os.path.exists(web_interface_dir):
                    print("❌ Web interface directory not found. Creating basic structure...")
                    return
                
                # Set up environment with correct PYTHONPATH
                env = os.environ.copy()
                env['PYTHONPATH'] = f"{novatrace_root}:{env.get('PYTHONPATH', '')}"
                    
                # Run reflex run command with proper flags
                if self.interface_logs:
                    # Show all logs when interface_logs=True
                    print("🚀 NovaTrace interface starting...")
                    print("   Frontend: http://localhost:3000")
                    print("   Backend:  http://localhost:8000")
                    print("   ✅ All Reflex logs will be shown below:")
                    print("   " + "="*50)
                    
                    # Use no redirection to show all logs
                    self.reflex_process = subprocess.Popen(
                        ["reflex", "run", "--env", "dev", "--loglevel", "debug"],
                        cwd=web_interface_dir,
                        env=env
                    )
                else:
                    # Hide logs when interface_logs=False (default)
                    DEVNULL = subprocess.DEVNULL
                    self.reflex_process = subprocess.Popen(
                        ["reflex", "run", "--env", "dev"],
                        cwd=web_interface_dir,
                        env=env,
                        stdout=DEVNULL,  # Hide stdout logs
                        stderr=DEVNULL,  # Hide stderr logs
                        text=True
                    )
                    print("🚀 NovaTrace interface starting...")
                    print("   Frontend: http://localhost:3000")
                    print("   Backend:  http://localhost:8000")
                
                # Wait a bit for the process to start
                import time
                time.sleep(2)
                
                if self.reflex_process.poll() is None:
                    print("   ✅ App running at: http://localhost:3000/")
                    if not self.interface_logs:
                        print("   💡 Use interface_logs=True to see detailed logs")
                else:
                    print("   ❌ Process failed to start")
                        
            except Exception as e:
                print(f"Warning: Could not start Reflex interface: {e}")
        
        # Start Reflex in a separate thread so it doesn't block the main application
        reflex_thread = threading.Thread(target=run_reflex, daemon=True)
        reflex_thread.start()
        
    def close(self):
        """
        Close the current session and connection to the database.
        Also stops the Reflex interface if it's running.
        Returns:
            None
        """
        self.session.close()
        
        # Stop Reflex interface if it's running
        if self.reflex_process and self.reflex_process.poll() is None:
            try:
                # First try graceful termination
                self.reflex_process.terminate()
                
                # Wait a bit for graceful shutdown
                import time
                time.sleep(2)
                
                # If still running, force kill
                if self.reflex_process.poll() is None:
                    self.reflex_process.kill()
                
                print("🛑 NovaTrace interface stopped")
                print("   Frontend and backend processes terminated")
            except Exception as e:
                print(f"Warning: Could not stop Reflex interface properly: {e}")

    def list_projects(self):
        """
        List all projects in the current session.
        """
        return self.session.query(Project).filter_by(session_id=self.active_session.id).all()
    
    def tokenizer(self, response) -> Dict[str, Union[int, float]]:
        """
        Tokenizer to calculate the number of tokens used in a response and their cost.
        Args:
            response: The response object from the LLM or agent.
        Returns:
            Dict[str, Union[int, float]]: A dictionary containing the number of input tokens,
                                          output tokens, total tokens
        """
        if hasattr(response, "usage"):
            prompt_tokens = response.usage.input_tokens
            completion_tokens = response.usage.output_tokens
            total_tokens = prompt_tokens + completion_tokens

            tokens = {
                "input_tokens": prompt_tokens,
                "output_tokens": completion_tokens,
                "total_tokens": total_tokens,
            }
        else:
            tokens = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            }
        return tokens
    
    def metadata(self, metadata: Dict[str, Union[str, float]]):
        """
        Set metadata for the current session.
        Args:
            metadata (Dict[str, Union[str, float]]): A dictionary containing metadata about the model
               - provider (str) | The provider of the model (e.g., "OpenAI", "Anthropic")
               - model (str) | The name of the model (e.g., "gpt-3.5-turbo", "claude-3-haiku-20240307")
               - input_cost_per_million_tokens (float) | Cost per million tokens for input
               - output_cost_per_million_tokens (float) | Cost per million tokens for output
        Raises:
            ValueError: If metadata is not a dictionary or does not contain the required keys.
        Returns:
            None
        """
        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a dictionary")
        
        self.provider = metadata.get('provider', None)
        self.model = metadata.get('model', None)
        self.input_cost_per_million_tokens = metadata.get('input_cost_per_million_tokens', 0.0)
        self.output_cost_per_million_tokens = metadata.get('output_cost_per_million_tokens', 0.0)

        if not all([self.provider, self.model, self.input_cost_per_million_tokens, self.output_cost_per_million_tokens]):
            raise ValueError("Metadata must contain 'provider', 'model', 'input_cost_per_million_tokens', and 'output_cost_per_million_tokens'")

    def set_user(self, user_id: str = None, user_name: str = None):
        """
        Set default user information for traces.
        Args:
            user_id (str, optional): External user ID.
            user_name (str, optional): External user name.
        Returns:
            None
        """
        self.user_external_id = user_id
        self.user_external_name = user_name

    def create_project(self, project_name: str):
        """
        Create a new project in the current session.
        Args:
            project_name (str): Name of the project to be created.
        Raises:
            ValueError: If a project with the same name already exists in the current session.
        Returns:
            None
        """
        existing_project = self.session.query(Project).filter_by(name=project_name, session_id=self.active_session.id).first()
        if existing_project:
            raise ValueError(f"Project '{project_name}' already exists in session '{self.active_session.name}'")
        self.project = Project(name=project_name, session_id=self.active_session.id, created_at=datetime.now(self.time_zone))

        self.session.add(self.project)
        self.session.commit()

    def connect_to_project(self, project_name: str):
        """
        Connect to an existing project in the current session.
        Args:
            project_name (str): Name of the project to connect to.
        Raises:
            ValueError: If the project with the specified name does not exist in the current session.
        Returns:
            Project: The project object if found.
        """
        self.project = self.session.query(Project).filter_by(name=project_name, session_id=self.active_session.id).first()
        if not self.project:
            raise ValueError(f"Project '{project_name}' not found in session '{self.active_session.name}'")
        return self.project

    def _get_named_args(self, func, *args, **kwargs):
        """
        Get named arguments from a function call.
        """
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        named_args = {}
        for name, value in bound_args.arguments.items():
            named_args[name] = {
                "type": type(value).__name__,
                "value": value
            }
        return named_args

    def _extract_user_info(self, func, *args, **kwargs):
        """
        Extract user information from function arguments.
        Looks for user_id, user_name, user, or context parameters.
        """
        try:
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            user_id = None
            user_name = None
            
            # Strategy 1: Direct user_id and user_name parameters
            if 'user_id' in bound_args.arguments:
                user_id = bound_args.arguments['user_id']
            if 'user_name' in bound_args.arguments:
                user_name = bound_args.arguments['user_name']
                
            # Strategy 2: From user object
            if 'user' in bound_args.arguments:
                user_obj = bound_args.arguments['user']
                if hasattr(user_obj, 'id'):
                    user_id = user_obj.id
                elif hasattr(user_obj, 'user_id'):
                    user_id = user_obj.user_id
                if hasattr(user_obj, 'name'):
                    user_name = user_obj.name
                elif hasattr(user_obj, 'username'):
                    user_name = user_obj.username
                    
            # Strategy 3: From context object
            if 'context' in bound_args.arguments:
                context_obj = bound_args.arguments['context']
                if hasattr(context_obj, 'user_id'):
                    user_id = context_obj.user_id
                if hasattr(context_obj, 'user_name'):
                    user_name = context_obj.user_name
                elif hasattr(context_obj, 'user') and hasattr(context_obj.user, 'name'):
                    user_name = context_obj.user.name
                    
            # Strategy 4: From request object (web frameworks)
            if 'request' in bound_args.arguments:
                request_obj = bound_args.arguments['request']
                if hasattr(request_obj, 'user'):
                    if hasattr(request_obj.user, 'id'):
                        user_id = request_obj.user.id
                    if hasattr(request_obj.user, 'name'):
                        user_name = request_obj.user.name
                        
            # Strategy 5: From kwargs
            if user_id is None and 'user_id' in kwargs:
                user_id = kwargs['user_id']
            if user_name is None and 'user_name' in kwargs:
                user_name = kwargs['user_name']
                
            # Use defaults if not found
            if user_id is None:
                user_id = self.user_external_id
            if user_name is None:
                user_name = self.user_external_name
                
            return str(user_id) if user_id else None, str(user_name) if user_name else None
            
        except Exception as e:
            print(f"Warning: Could not extract user info: {e}")
            return self.user_external_id, self.user_external_name

    def _get_trace_type_id(self, type_name):
        """Get trace type ID by name."""
        try:
            trace_type = self.session.query(TraceTypes).filter_by(name=type_name).first()
            if trace_type:
                return trace_type.id
            else:
                # Fallback IDs if not found
                fallback_ids = {"LLM": 1, "Agent": 2, "Tool": 3}
                return fallback_ids.get(type_name, 1)
        except Exception as e:
            print(f"Error getting trace type ID for {type_name}: {e}")
            # Fallback IDs
            fallback_ids = {"LLM": 1, "Agent": 2, "Tool": 3}
            return fallback_ids.get(type_name, 1)

    def _log_trace(self, type_id: int, input_data, output_data, request_time, response_time,
                    input_tokens=0, output_tokens=0, model_name=None, model_provider=None,
                    user_external_id=None, user_external_name=None):
        """
        Log a trace for the current request.
        Args:
            type_id (int): Type of trace (1 for LLM, 2 for Agent, 3 for Tool).
            input_data: Input data for the trace.
            output_data: Output data for the trace.
            request_time (datetime): Time when the request was made.
            response_time (datetime): Time when the response was received.
            input_tokens (int, optional): Number of input tokens used. Defaults to 0.
            output_tokens (int, optional): Number of output tokens used. Defaults to 0.
            user_external_id (str, optional): External user ID. Defaults to None.
            user_external_name (str, optional): External user name. Defaults to None.
        Returns:
            None
        Raises:
            None
        """
        duration = (response_time - request_time).total_seconds() * 1000  # ms
        trace = Trace(
            type_id=type_id,
            input_data=json.dumps(input_data, default=str),
            output_data=json.dumps(output_data, default=str),
            project_id=self.project.id,
            created_at=response_time,
            request_time=request_time,
            response_time=response_time,
            duration_ms=duration,
            input_tokens=input_tokens,
            output_tokens=output_tokens,

            model_provider=model_provider if model_provider else self.provider,
            model_name=model_name if model_name else self.model,
            model_input_cost=self.input_cost_per_million_tokens,
            model_output_cost=self.output_cost_per_million_tokens,
            call_cost = ((input_tokens * (self.input_cost_per_million_tokens/1000000)) + (output_tokens * (self.output_cost_per_million_tokens/1000000))),
            
            # Add user information
            user_external_id=user_external_id,
            user_external_name=user_external_name
        )
        self.session.add(trace)
        self.session.commit()

    def llm(self, func):
        """
        Decorator to trace LLM calls.
        Args:
            func: The function to be traced.
        Returns:
            function: The wrapped function that logs the trace.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_time = datetime.now(self.time_zone)
            
            # Extract user information before function call
            user_id, user_name = self._extract_user_info(func, *args, **kwargs)
            
            result = func(*args, **kwargs)
            response_time = datetime.now(self.time_zone)
            try:
                _args = self._get_named_args(func, *args, **kwargs)
            except Exception as e:
                _args = {"args": args}
            self._log_trace(self._get_trace_type_id("LLM"), {"args": _args},
                            result, request_time, response_time,
                            model_name=kwargs.get("model_name", self.model),
                            model_provider=kwargs.get("model_provider", self.provider),
                            input_tokens=kwargs.get("input_tokens", 0),
                            output_tokens=kwargs.get("output_tokens", 0),
                            user_external_id=user_id,
                            user_external_name=user_name
                            )
            return result
        return wrapper

    def agent(self, func):
        """
        Decorator to trace agent calls.
        Args:
            func: The function to be traced.
        Returns:
            function: The wrapped function that logs the trace. 
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_time = datetime.now(self.time_zone)
            
            # Extract user information before function call
            user_id, user_name = self._extract_user_info(func, *args, **kwargs)
            
            result = func(*args, **kwargs)
            tokens = self.tokenizer(result)
            response_time = datetime.now(self.time_zone)
            try:
                _args = self._get_named_args(func, *args, **kwargs)
            except Exception as e:
                _args = {"args": args}
            self._log_trace(self._get_trace_type_id("Agent"), {"args": _args}, 
                            result, request_time, response_time,
                            tokens.get("input_tokens", 0),
                            tokens.get("output_tokens", 0),
                            model_name=kwargs.get("model_name", self.model),
                            model_provider=kwargs.get("model_provider", self.provider),
                            user_external_id=user_id,
                            user_external_name=user_name
                            )
            return result
        return wrapper

    def tool(self, func):
        """ 
        Decorator to trace tool calls.
        Args:
            func: The function to be traced.
        Returns:
            function: The wrapped function that logs the trace.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_time = datetime.now(self.time_zone)
            
            # Extract user information before function call
            user_id, user_name = self._extract_user_info(func, *args, **kwargs)
            
            result = func(*args, **kwargs)
            try:
                result_raw = result[-1]['result']
                result_text = result_raw[0].text if isinstance(result_raw, list) and result_raw else ""

            except Exception as e:
                result_text = result

            response_time = datetime.now(self.time_zone)
            try:
                _args = self._get_named_args(func, *args, **kwargs)
            except Exception as e:
                _args = {"args": args}
            self._log_trace(self._get_trace_type_id("Tool"), {"args": _args}, 
                            str(result_text), request_time, response_time,
                            user_external_id=user_id,
                            user_external_name=user_name
                            )
            return result
        return wrapper