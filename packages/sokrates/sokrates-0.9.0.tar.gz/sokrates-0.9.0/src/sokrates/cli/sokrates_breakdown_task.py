#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from sokrates.refinement_workflow import RefinementWorkflow
from sokrates.colors import Colors
from sokrates.file_helper import FileHelper
from sokrates.output_printer import OutputPrinter
from sokrates.config import Config

DEFAULT_MAX_TOKENS = 20000

def main():
    """Main function for the task breakdown CLI tool.
    
    This function handles command-line arguments, processes the input task,
    and executes the breakdown workflow using the RefinementWorkflow.
    
    Returns:
        None
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
            description='Breaks down a given task into sub-tasks with complexity rating. Returns a json representation of the calculated tasks.',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

    parser.add_argument(
        '--api-endpoint',
        default=None,
        help=f"LLM server API endpoint. Default is {Config.DEFAULT_API_ENDPOINT}"
    )

    parser.add_argument(
        '--api-key',
        required=False,
        default=None,
        help='API key for authentication (many local servers don\'t require this)'
    )

    parser.add_argument(
        '--task', '-t',
        required=False,
        default=None,
        help='The full task description at hand as string'
    )

    parser.add_argument(
        '--task-file', '-tf',
        required=False,
        default=None,
        help='A filepath to a file with the task to break down'
    )
    
    parser.add_argument(
        '--model', '-m',
        default=None,
        help=f"The model to use for the task breakdown (default: {Config.DEFAULT_MODEL})"
    )
    
    parser.add_argument(
        '--temperature',
        default=None,
        help=f"The temperature to use for the task breakdown (default: {Config.DEFAULT_MODEL_TEMPERATURE})"
    )

    parser.add_argument(
        '--output', '-o',
        help='Output filename to save the response (e.g., tasks.json)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with debug information'
    )
    
    # context
    parser.add_argument(
        '--context-text', '-ct',
        default=None,
        help='Optional additional context text to prepend before the prompt'
    )
    parser.add_argument(
        '--context-files', '-cf',
        help='Optional comma separated additional context text file paths with content that should be prepended before the prompt'
    )
    parser.add_argument(
        '--context-directories', '-cd',
        default=None,
        help='Optional comma separated additional directory paths with files with content that should be prepended before the prompt'
    )

    # Parse arguments
    args = parser.parse_args()
    config = Config(verbose=args.verbose)
    
    api_key = config.api_key
    if args.api_key:
        api_key = args.api_key
        
    api_endpoint = config.api_endpoint
    if args.api_endpoint:
        api_endpoint = args.api_endpoint

    model = config.default_model
    if args.model:
        model = args.model
        
    temperature = config.default_model_temperature
    if args.temperature:
        temperature = args.temperature

    if args.task and args.task_file:
        OutputPrinter.print_error("You cannot provide both a task-file and a task. Exiting.")
        sys.exit(1)
        
    if not args.task and not args.task_file:
        OutputPrinter.print_error("You did not provide a task via --task or --task-file. Exiting.")
        sys.exit(1)
        
    if not args.api_key:
        api_key = 'notrequired'
    
    task = ""
    if args.task:
        task = args.task
        
    if args.task_file:
        task = FileHelper.read_file(args.task_file, verbose=args.verbose)
        
    # context
    context_array = []
    if args.context_text:
        context_array.append(args.context_text)
        OutputPrinter.print_info("Appending context text to prompt:", args.context_text , Colors.BRIGHT_MAGENTA)
    if args.context_directories:
        directories = [s.strip() for s in args.context_directories.split(",")]
        context_array.extend(FileHelper.read_multiple_files_from_directories(directories, verbose=args.verbose))
        OutputPrinter.print_info("Appending context directories to prompt:", args.context_directories , Colors.BRIGHT_MAGENTA)
    if args.context_files:
        files = [s.strip() for s in args.context_files.split(",")]
        context_array.extend(FileHelper.read_multiple_files(files, verbose=args.verbose))
        OutputPrinter.print_info("Appending context files to prompt:", args.context_files , Colors.BRIGHT_MAGENTA)
    
        
    workflow = RefinementWorkflow(api_endpoint=api_endpoint, 
        api_key=api_key, model=model, 
        max_tokens=DEFAULT_MAX_TOKENS, 
        temperature=temperature,
        verbose=args.verbose
    )
    result = workflow.breakdown_task(task=task, model=model, context_array=context_array)

    OutputPrinter.print_section("RESULT", Colors.BRIGHT_BLUE, "═")
    print(result)
    
    if args.output:
        OutputPrinter.print_info("Writing task list to file:", args.output, Colors.BRIGHT_MAGENTA)
        FileHelper.write_to_file(args.output, result, verbose=args.verbose)
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Process interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
        sys.exit(1)
