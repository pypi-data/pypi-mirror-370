import argparse
import sys
from pathlib import Path
from marsa.pipeline import AspectSentimentPipeline
from marsa.export import export_for_review

def analyze_text(args) -> int:
    """
    Analyze a single text string for aspects and sentiment.
    
    Args:
        args: Parsed command line arguments containing:
            - text (str): The text to analyze
            - config (str): Path to aspect configuration file
            - context_window (int): Number of tokens before/after aspects for context
            - output (str, optional): Output file path for results
    
    Returns:
        int: Exit code (0 for success, 1 for error)
        
    Raises:
        Exception: If analysis fails due to configuration or processing errors
    """
    config = args.config
    if not Path(config).resolve().exists():
        print(f"Error: Config file '{config}' does not exist")
        return 1
    
    try:
        pipeline = AspectSentimentPipeline(config_file=config, context_window=args.context_window)
        results = pipeline.process_corpus_flat([args.text])
        
        if args.output:
            export_for_review(results, args.output)
            print(f"Results saved to {args.output}")
        else:
            result = results[0]
            print(f"\nText: {result['original_text']}")
            print(f"Aspects found: {result['aspects_found']}")
            print(f"Context window: {args.context_window} tokens")
            
            if result['aspect_sentiments']:
                print("\nAspect Analysis:")
                for aspect in result['aspect_sentiments']:
                    print(f"  • {aspect['aspect']} ({aspect['category']}): {aspect['sentiment']}")
                    if aspect['confidence']:
                        print(f"    Confidence: {aspect['confidence']:.2f}")
            else:
                print("No aspects detected.")
        
        return 0
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1

def analyze_file(args) -> int:
    """
    Analyze multiple text comments from a file for aspects and sentiment.
    
    Processes a file containing one comment per line and performs aspect-based
    sentiment analysis on each comment using the specified configuration.
    
    Args:
        args: Parsed command line arguments containing:
            - input_file (str): Path to input file (one comment per line)
            - config (str): Path to aspect configuration file
            - context_window (int): Number of tokens before/after aspects for context
            - output (str): Output file path for results
    
    Returns:
        int: Exit code (0 for success, 1 for error)
        
    Raises:
        Exception: If file processing or analysis fails
    """
    input_file = args.input_file
    input_path = Path(input_file).resolve()
    config = args.config
    output = args.output

    if not input_path.exists():
        print(f"Error: Input file '{input_file}' does not exist")
        return 1
        
    if not Path(config).resolve().exists():
        print(f"Error: Config file '{config}' does not exist")
        return 1
    
    print(f"Analyzing {input_file} with config {config}")
    print(f"Using context window: {args.context_window} tokens")
    
    try:
        pipeline = AspectSentimentPipeline(config_file=config, context_window=args.context_window)
        
        with open(input_path, 'r', encoding='utf-8') as fp:
            comments = [line.strip() for line in fp if line.strip()]
        
        if not comments:
            print("Warning: No comments found in input file")
            return 1
            
        print(f"Processing {len(comments)} comments...")
        
        if len(comments) > 10:
            print("Processing", end="", flush=True)
        
        results = pipeline.process_corpus_flat(comments)
        
        if len(comments) > 10:
            print(" ✓")
        
        export_for_review(results, output)
        
        total_aspects = sum(r['aspects_found'] for r in results)
        print(f"Analysis complete!")
        print(f"  - Processed: {len(comments)} comments")
        print(f"  - Found: {total_aspects} aspects total")
        print(f"  - Context window: {args.context_window} tokens")
        print(f"  - Results saved to: {output}")
        
        return 0
    
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1

def main():
    """
    Main entry point for the MARSA command-line interface.
    
    Sets up argument parsing for analyze-text and analyze-file commands,
    configures help text and examples, and executes the appropriate
    analysis function based on user input.
    """
    parser = argparse.ArgumentParser(
        description='MARSA - Multi-aspect sentiment analysis tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  marsa analyze-text "Great camera but poor battery" -c config.yaml -w 2
  marsa analyze-file reviews.txt -c config.yaml -o results.json
  marsa analyze-text "Love this phone!" -c config.yaml --output analysis.json --context_window 3
  
Context Window:
  The context window determines how many tokens before and after each detected aspect
  are included for sentiment analysis. For example, in "I love the camera but really hate the battery":
  - "camera" is at token position 4
  - With context window 2: includes tokens "love the" (before) and "but really" (after)
  - This gives the model more surrounding context to determine sentiment accurately
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze single text command
    text_parser = subparsers.add_parser(
        'analyze-text', 
        help='Analyze a single text string',
        aliases=['text']
    )
    text_parser.add_argument('text', help='Text to analyze')
    text_parser.add_argument('-c', '--config', required=True, 
                           help='Aspect config file (.yaml/.yml or .json)')
    text_parser.add_argument('-o', '--output', 
                           help='Output file (if not provided, prints to console)')
    text_parser.add_argument('-w', '--context-window', type=int, default=3, metavar='N',
                       help='Number of tokens before and after each aspect to include for sentiment analysis (default: 3)')
    text_parser.set_defaults(func=analyze_text)
    
    # Analyze file command  
    file_parser = subparsers.add_parser(
        'analyze-file',
        help='Analyze aspects and sentiment in a file of comments',
        aliases=['file']
    )
    file_parser.add_argument('input_file', help='Input file (one comment per line)')
    file_parser.add_argument('-c', '--config', required=True, 
                           help='Aspect config file (.yaml/.yml or .json)')
    file_parser.add_argument('-o', '--output', default='results.json', 
                           help='Output file (default: results.json)')
    file_parser.add_argument('-w', '--context-window', type=int, default=3, metavar='N',
                           help='Number of tokens before and after each aspect to include for sentiment analysis (default: 3)')
    file_parser.set_defaults(func=analyze_file)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        exit_code = args.func(args)
        sys.exit(exit_code or 0)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()