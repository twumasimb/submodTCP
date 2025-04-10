import os
import datetime
import logging

def setup_logging(method: str, args) -> logging.Logger:
    """
    Set up logging configuration for the experiment.
    
    Args:
        method: Prioritization method being used
        args: Command line arguments
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs"))
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create a timestamp for the log filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create unique identifiers based on arguments
    seed_str = f"seed{args.seed}" if args.seed is not None else "noseed"
    run_str = "run" if hasattr(args, 'run') and args.run else "norun"
    eval_str = "eval" if hasattr(args, 'evaluate') and args.evaluate else "noeval"
    
    # Construct log filename
    log_filename = f"{method}_{seed_str}_{run_str}_{eval_str}_{timestamp}.log"
    log_path = os.path.join(logs_dir, log_filename)
    
    # Configure logging
    logger = logging.getLogger("test_prioritization")
    logger.setLevel(logging.INFO)
    
    # File handler for logging to file
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    
    # Console handler for logging to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logging initialized for experiment: {method}")
    logger.info(f"Command line arguments: {vars(args)}")
    
    return logger

def setup_logger(name: str) -> logging.Logger:
    """
    Set up a simple logger for a specific component.
    
    Args:
        name: Name of the logger/component
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs"))
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create a timestamp for the log filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Construct log filename
    log_filename = f"{name}_{timestamp}.log"
    log_path = os.path.join(logs_dir, log_filename)
    
    # Configure logging
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # File handler for logging to file
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    
    # Console handler for logging to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logger initialized for: {name}")
    
    return logger