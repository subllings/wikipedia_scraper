# src/main.py

import time
from src.leaders_scraper import WikipediaScraper
from utils.print_utils import PrintUtils, BgColor, Color
from utils.output_format import OutputFormat


def run_scraper(use_multithreading=False, output_format=OutputFormat.JSON):
    """
    Run the Wikipedia scraping pipeline with optional multithreading.

    Parameters:
    - use_multithreading (bool): If True, fetch leaders using multithreading.
    """
    bg_color = BgColor.BLUE if use_multithreading else BgColor.GREEN
    PrintUtils.print_bg_color(f"Run scraper (multithreading={use_multithreading})", bg_color)
    
    scraper = WikipediaScraper()

    start_time = time.time()

    # limit_per_country ===========================================================================
    scraper.fetch_leaders(limit_per_country=5, verbose=True, use_multithreading=use_multithreading)
    # limit_per_country ===========================================================================

    # Store to JSON, CSV or both
    if output_format == OutputFormat.JSON:
        scraper.to_json_file("leaders_data.json")
    elif output_format == OutputFormat.CSV:
        scraper.to_csv_file("leaders_data.csv")
    elif output_format == OutputFormat.JSON_AND_CSV:
        scraper.to_json_file("leaders_data.json")
        scraper.to_csv_file("leaders_data.csv")
    else:
        PrintUtils.print_color(f"[ERROR] Unsupported output format: {output_format}", Color.RED)

    duration = time.time() - start_time
    print("\n")
    PrintUtils.print_bg_color(f"Execution time (multithreading={use_multithreading}): {duration:.2f} seconds",bg_color)
    print("\n")
    
    return duration

# Main function that runs the scraping pipeline
def main():

    # Run with multithreading enabled
    use_multithreading = True
    exec_time_thread_true = run_scraper(use_multithreading=use_multithreading, output_format=OutputFormat.JSON_AND_CSV)

    # Run with multithreading disabled
    use_multithreading = False
    exec_time_thread_false = run_scraper(use_multithreading=use_multithreading, output_format=OutputFormat.JSON_AND_CSV)

    # Display comparison
    PrintUtils.print_color("\nExecution Time Comparison:", Color.CYAN)
    PrintUtils.print_bg_color(f"- With multithreading:    {exec_time_thread_true:.2f} seconds", BgColor.BLUE)
    PrintUtils.print_bg_color(f"- Without multithreading: {exec_time_thread_false:.2f} seconds", BgColor.GREEN)

    # Optional: compute and print the speed gain
    if exec_time_thread_false > exec_time_thread_true:
        gain = exec_time_thread_false / exec_time_thread_true
        PrintUtils.print_color(f"\nMultithreading was ~{gain:.2f}x faster\n", Color.MAGENTA)
    else:
        PrintUtils.print_color(
        "\nMultithreading was slower — the API might be blocking concurrent requests.\n"
        "Sequential execution may be more efficient when servers limit parallel access.",
        Color.MAGENTA
    )

# Entry point of the script when executed directly (e.g., python main.py)
if __name__ == "__main__":
    main()
