"""Command-line interface for the Results Parser Agent."""

import asyncio
import json
import sys
from pathlib import Path

import typer
from loguru import logger

from .agent.parser_agent import ResultsParserAgent
from .config.settings import ParserConfig, settings
from .models.schema import StructuredResults


def setup_logging(verbose: bool, log_level: str = "INFO") -> None:
    """Setup logging configuration."""
    # Remove default handler
    logger.remove()

    # Add console handler
    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    if verbose:
        log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"

    logger.add(sys.stderr, format=log_format, level=log_level, colorize=True)


def validate_input_path(input_path: str) -> Path:
    """Validate and return input path."""
    path = Path(input_path)
    if not path.exists():
        raise typer.BadParameter(f"Input path does not exist: {input_path}")
    return path


def validate_metrics(metrics: list[str]) -> list[str]:
    """Validate metrics list."""
    if not metrics:
        raise typer.BadParameter("At least one metric must be specified")
    return [metric.strip() for metric in metrics]


def load_config(
    provider: str | None = None,
    model: str | None = None,
) -> ParserConfig:
    """Load configuration from environment variables and CLI options.

    Priority order (highest to lowest):
    1. Command line options
    """

    config = settings

    # Override with CLI options if provided
    if provider:
        config.LLM_PROVIDER = provider
        logger.info(f"🔧 Overriding provider to: {provider}")

    if model:
        config.LLM_MODEL = model
        logger.info(f"🔧 Overriding model to: {model}")

    return config


def save_output(
    results: StructuredResults, output_path: str, pretty_print: bool = True
) -> None:
    """Save results to output file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        if pretty_print:
            json.dump(results.model_dump(), f, indent=2)
        else:
            json.dump(results.model_dump(), f)

    logger.info(f"💾 Results saved to: {output_file}")


def analyze_results(results: StructuredResults, requested_metrics: list[str]) -> None:
    """Analyze and log the results for better user feedback."""
    if not results.iterations:
        logger.warning("⚠️  No data extracted from the input files")
        logger.info("🔍 This could indicate:")
        logger.info("   - Requested metrics don't exist in the data")
        logger.info("   - Files are empty or don't contain the expected format")
        logger.info("   - Directory structure doesn't match expected pattern")
        logger.info("💡 Try:")
        logger.info("   - Check if the requested metrics exist in your data files")
        logger.info("   - Verify the input path contains the expected file structure")
        logger.info("   - Use --verbose flag for detailed debugging information")
        return

    # Analyze extracted data
    total_iterations = len(results.iterations)
    total_instances = sum(len(iter.instances) for iter in results.iterations)
    total_metrics = sum(
        len(inst.statistics) for iter in results.iterations for inst in iter.instances
    )

    # Check if all requested metrics were found
    extracted_metric_names = set()
    for iter in results.iterations:
        for inst in iter.instances:
            for stat in inst.statistics:
                extracted_metric_names.add(stat.metricName)

    missing_metrics = set(requested_metrics) - extracted_metric_names
    found_metrics = set(requested_metrics) & extracted_metric_names

    logger.info("📊 Results Analysis:")
    logger.info(f"   - Iterations processed: {total_iterations}")
    logger.info(f"   - Instances processed: {total_instances}")
    logger.info(f"   - Total metrics extracted: {total_metrics}")

    if found_metrics:
        logger.info(
            f"✅ Successfully extracted metrics: {', '.join(sorted(found_metrics))}"
        )

    if missing_metrics:
        logger.warning(
            f"⚠️  Requested metrics not found: {', '.join(sorted(missing_metrics))}"
        )
        logger.info(
            "💡 These metrics may not exist in your data files or may have different names"
        )


app = typer.Typer(
    name="result-parser",
    help="Results Parser Agent - Extract metrics from raw result files",
    add_completion=False,
)


@app.command()
def main(
    input_path: str = typer.Argument(
        ..., help="Path to result file or directory containing result files to parse"
    ),
    metrics: str = typer.Option(
        ...,
        "--metrics",
        "-m",
        help="Comma-separated list of metrics to extract (required, e.g., 'RPS,latency,throughput')",
    ),
    provider: str | None = typer.Option(
        None,
        "--provider",
        help="LLM provider (groq, openai, anthropic, google, ollama). Can also be set via LLM_PROVIDER environment variable.",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        help="LLM model name (e.g., llama3.1-8b-instant, gpt-4, claude-3-sonnet). Can also be set via LLM_MODEL environment variable.",
    ),
    output: str = typer.Option(
        "results.json",
        "--output",
        "-o",
        help="Output JSON file path (default: results.json)",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging and pretty print output"
    ),
    log_level: str = typer.Option(
        "INFO", "--log-level", help="Logging level", case_sensitive=False
    ),
) -> None:
    """
    Results Parser Agent - Extract metrics from raw result files.

    This tool intelligently parses result files and extracts specified metrics
    into structured JSON output. It supports various file formats and can handle
    large, unstructured result files.

    Environment Variables:
        LLM_PROVIDER: Set default LLM provider (e.g., openai, groq, anthropic, google)
        LLM_MODEL: Set default LLM model (e.g., gpt-4o, llama3.1-8b-instant)

    Examples:

        # Parse all files in a directory with default configuration
        result-parser ./benchmark_results --metrics "RPS,latency" --output results.json

        # Parse a single file with custom configuration
        result-parser ./specific_result.txt --metrics "accuracy,precision" --provider openai --model gpt-4

        # Override specific settings
        result-parser ./results --metrics "RPS" --provider groq --model llama3.1-70b-versatile

        # Verbose output with pretty-printed JSON
        result-parser ./results --metrics "RPS" --verbose

        # Use environment variables for LLM settings
        export LLM_PROVIDER=openai
        export LLM_MODEL=gpt-4o
        result-parser ./results --metrics "RPS,throughput"
    """
    try:
        # Setup logging
        setup_logging(verbose, log_level)

        # Validate input path
        if not input_path:
            raise typer.BadParameter("Input path must be specified")
        validate_input_path(input_path)

        # Validate metrics
        metrics_list = validate_metrics([m.strip() for m in metrics.split(",")])

        # Pretty print is the opposite of verbose (verbose = pretty, non-verbose = compact)
        pretty_print = verbose

        # Load and modify configuration
        load_config(
            provider=provider,
            model=model,
        )

        # Run the agent
        async def run_agent() -> StructuredResults:
            agent = ResultsParserAgent()
            results = await agent.parse_results(
                input_path=input_path, metrics=metrics_list
            )
            return results

        # Execute async function
        results = asyncio.run(run_agent())

        # Analyze results for better user feedback
        analyze_results(results, metrics_list)

        # Save results to file
        save_output(results, output, pretty_print)

        if results.iterations:
            logger.info("🎉 Parsing completed successfully")
        else:
            logger.warning("⚠️  Parsing completed but no data was extracted")

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if verbose:
            logger.exception("🔍 Full traceback:")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
