import warnings
import traceback

def custom_warning_handler(message, category, filename, lineno, file=None, line=None):
    """Custom warning handler that prints full traceback."""
    print(f"\n{category.__name__}: {message} ({filename}, line {lineno})")
    print("Full traceback (most recent call first):")
    traceback.print_stack()

warnings.showwarning = custom_warning_handler
