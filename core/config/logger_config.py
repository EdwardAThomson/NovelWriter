import logging
import os
# from datetime import datetime # No longer needed for filename timestamp

def setup_app_logger(name='NovelWriterApp', output_dir='.', level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent log messages from propagating to the root logger,
    # which might have its own handlers and cause duplicate console output.
    logger.propagate = False

    # Clear existing handlers from this specific logger
    # This is important if this function could be called multiple times for the same logger instance.
    if logger.hasHandlers():
        logger.handlers.clear()

    # --- Console Handler ---
    # Outputs log messages to the console (stderr by default).
    ch = logging.StreamHandler()
    ch.setLevel(level) # Set the level for this handler.
    
    # Define the format for log messages.
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch) # Add the console handler to the logger.

    # --- File Handler (Modified for fixed filename and append mode) ---
    # Ensures the output directory exists.
    os.makedirs(output_dir, exist_ok=True)
    
    # Use a fixed filename for the log file.
    log_filename = "application.log"
    log_filepath = os.path.join(output_dir, log_filename)

    # Check if we are appending or creating a new file for the initial log message.
    # This check is done BEFORE the handler is added, so the first message from this setup
    # will accurately reflect the state.
    is_new_file = not os.path.exists(log_filepath) or os.path.getsize(log_filepath) == 0

    # Create a file handler.
    # The default mode for FileHandler is 'a' (append), which creates the file if it doesn't exist.
    fh = logging.FileHandler(log_filepath, mode='a', encoding='utf-8')
    fh.setLevel(level) # Set the level for this handler.
    fh.setFormatter(formatter) # Use the same formatter as the console handler.
    logger.addHandler(fh) # Add the file handler to the logger.

    # Log the initialization status.
    if is_new_file:
        logger.info(f"Logger '{name}' initialized. Logging to console and new file: {log_filepath}")
    else:
        logger.info(f"Logger '{name}' initialized. Logging to console and appending to existing file: {log_filepath}")
        
    return logger

if __name__ == '__main__':
    # Example usage for testing the logger_config module directly.
    # This will create a logger that outputs to console and 'test_app_log.log' in the current directory.
    
    # Create a 'logs' subdirectory for the test if it doesn't exist
    test_log_dir = "test_logs"
    os.makedirs(test_log_dir, exist_ok=True)

    print(f"Testing logger setup. Log file will be in: {os.path.abspath(test_log_dir)}")

    # First setup (should create or append to 'test_logs/application.log')
    logger1 = setup_app_logger(name="TestApp1", output_dir=test_log_dir, level=logging.DEBUG)
    logger1.debug("Debug message from TestApp1.")
    logger1.info("Info message from TestApp1.")
    logger1.warning("Warning message from TestApp1.")

    # Simulate re-running the app or setting up another logger instance (should append)
    logger2 = setup_app_logger(name="TestApp2", output_dir=test_log_dir, level=logging.INFO)
    logger2.info("Info message from TestApp2 - this should append to the same file.")
    logger2.error("Error message from TestApp2.")

    print(f"Test complete. Check the log file: {os.path.join(test_log_dir, 'application.log')}") 