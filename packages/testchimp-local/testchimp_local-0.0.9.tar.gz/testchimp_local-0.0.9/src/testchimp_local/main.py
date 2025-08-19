import os 
import asyncio
import sys
import logging
import time

logger = logging.getLogger(__name__)

def setup_logging():
    """
    Sets up logging to write to both console and a timestamp-based log file.
    The log file will be named testchimp_run_<timestamp>.log in the current directory.
    """
    try:
        # Get the root logger to configure all loggers
        root_logger = logging.getLogger()
        
        # Clear any existing handlers to avoid duplicates
        root_logger.handlers.clear()
        
        # Set the log level
        root_logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Create file handler with timestamp
        timestamp = int(time.time())
        log_filename = f"testchimp_run_{timestamp}.log"
        
        try:
            file_handler = logging.FileHandler(log_filename, mode='w')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            
            # Add both handlers to the root logger
            root_logger.addHandler(console_handler)
            root_logger.addHandler(file_handler)
            
            # Log a clear message about the log file location
            print(f"\nLOG FILE: {os.path.abspath(log_filename)}\n")
            logger.info(f"Logger configured to write to {log_filename}")
            
        except Exception as file_error:
            # If file logging fails, fall back to console-only logging
            print(f"Warning: Could not create log file {log_filename}: {file_error}")
            print("Falling back to console-only logging")
            root_logger.addHandler(console_handler)
            logger.info("Logger configured for console-only output (file logging failed)")
            
    except Exception as e:
        # If logging setup completely fails, at least ensure basic console output
        print(f"Error setting up logging: {e}")
        print("Using basic console logging")
        basic_logger = logging.getLogger()
        basic_logger.setLevel(logging.INFO)
        basic_handler = logging.StreamHandler(sys.stdout)
        basic_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        basic_logger.addHandler(basic_handler)

def main():
    # Setup logging first, before any other operations
    setup_logging()
    
    import argparse
    from .server import start_server
    from .feature_facade import FeatureFacade, set_feature_facade_instance
    from .explore_runner import run_exploration_from_file

    parser = argparse.ArgumentParser(description="Local AI QA Agent CLI. Supports both prompt-based and script-based exploration configs.")
    parser.add_argument("--port", type=int, default=43449, help="Port to run the server on")
    parser.add_argument("--env", type=str, default=".env.prod", help="Path to env file")
    parser.add_argument("--mcp", action="store_true", help="Run as MCP stdin server (future)")
    parser.add_argument("--config_file", type=str, help="Path to exploration config JSON file for one-off run")

    args = parser.parse_args()

    if args.mcp:
        logger.info("MCP mode is not yet implemented.")
        sys.exit(1)
    
    try:
        facade = FeatureFacade(args.env)
        set_feature_facade_instance(facade)
        auth_response = facade.authenticate()
        api_key = auth_response.apiKey
        version_evaluation = auth_response.clientVersionEvaluation
        
        # Handle version evaluation
        if version_evaluation and version_evaluation.result:
            from .feature_facade import VersionEvaluationResult
            
            if version_evaluation.result == VersionEvaluationResult.HAS_NEWER_VERSION:
                logger.info(f"⚠️  Version Update Recommended: {version_evaluation.helpMessage}. Run: pip install --upgrade testchimp-local")
            elif version_evaluation.result == VersionEvaluationResult.IS_UNSUPPORTED_VERSION:
                logger.info(f"❌ Unsupported Version: {version_evaluation.helpMessage}")
                logger.info("Please update to the latest version to continue. Run pip install --upgrade testchimp-local")
                sys.exit(1)
            elif version_evaluation.result == VersionEvaluationResult.UNKNOWN_EVALUATION_RESULT:
                logger.info(f"⚠️  Version Check: {version_evaluation.helpMessage}")
        
        # If config file is provided, run one-off exploration
        if args.config_file:
            logger.info(f"Running one-off exploration with config: {args.config_file}")
            result = asyncio.run(run_exploration_from_file(args.config_file, api_key))
            logger.info(f"Exploration completed: {result}")
            return
        else:
            # Start server mode
            start_server(args, api_key, facade)
            
    except Exception as e:
        logger.info(f"Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()