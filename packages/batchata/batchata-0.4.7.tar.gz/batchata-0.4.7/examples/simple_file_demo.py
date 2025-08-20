"""Simple file demo with file and prompt for citations."""

import tempfile
import os
import random
import sys
from pathlib import Path
from batchata import Batch
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class InvoiceAnalysis(BaseModel):
    """Structured output for invoice analysis."""
    invoice_number: str
    total_amount: float
    vendor: str
    payment_status: str


def generate_invoice_content(invoice_num: int) -> str:
    """Generate simple invoice content with random data."""
    vendor = random.choice(["Acme Corp", "Tech Solutions", "Office Supplies"])
    total = random.randint(100, 1000)
    status = random.choice(["PAID", "PENDING", "OVERDUE"])
    
    return f"""INVOICE #INV-2024-{invoice_num:03d}
Vendor: {vendor}
Total: ${total}.00
Payment Status: {status}"""


def create_temp_invoice_files():
    """Create temporary invoice files for testing."""
    temp_dir = tempfile.mkdtemp(prefix="batchata_invoices_")
    
    files = []
    for i in range(1, 4):
        filepath = Path(temp_dir) / f"invoice_{i:03d}.txt"
        content = generate_invoice_content(i)
        filepath.write_text(content)
        files.append(filepath)
    
    return files, temp_dir


def main():
    """Run invoice processing demo with file and prompt."""
    # Create temporary invoice files
    invoice_files, temp_dir = create_temp_invoice_files()
    
    try:
        # Create batch configuration
        batch = (
            Batch(results_dir="./examples/file_output", max_parallel_batches=1, items_per_batch=1)
            .set_state(file="./examples/demo_file_state.json", reuse_state=False)
            .set_default_params(model="claude-sonnet-4-20250514", temperature=0.7)
            .add_cost_limit(usd=5.0)
            .set_verbosity("warn")
        )
        
        # Add jobs using file and prompt
        for invoice_file in invoice_files:
            batch.add_job(
                file=invoice_file,
                prompt="Extract the invoice number, total amount, vendor name, and payment status.",
                response_model=InvoiceAnalysis,
                enable_citations=True
            )
        
        # Execute batch
        print("Starting batch processing...")
        def progress_callback(s, t, b):
            print(f"\rProgress: {s['completed']}/{s['total']} jobs | "\
                  f"Batches: {s['batches_completed']}/{s['batches_total']} (pending: {s['batches_pending']}) | " \
                  f"Cost: ${round(s['cost_usd'],3)}/{s['cost_limit_usd']} | " \
                  f"Items per batch: {s['items_per_batch']} | Time: {round(t, 2)}s", end="")
            sys.stdout.flush()
        
        run = batch.run(on_progress=progress_callback)
        
        # Get results
        run.status(print_status=True)
        results = run.results()
        
        # Display results
        print("\nResults:")
        
        # Show successful results
        for result in results["completed"]:
            analysis = result.parsed_response
            print(f"\nJob {result.job_id}:")
            print(f"  Invoice: {analysis.invoice_number}")
            print(f"  Vendor: {analysis.vendor}")
            print(f"  Total: ${analysis.total_amount:.2f}")
            print(f"  Status: {analysis.payment_status}")
            
            # Show citations if available
            if result.citations:
                print(f"  Citations found: {len(result.citations)}")
                for i, citation in enumerate(result.citations[:2]):
                    print(f"    - {citation.text[:50]}...")
        
        # Show failed results
        for result in results["failed"]:
            print(f"\nJob {result.job_id} failed: {result.error}")
        
        # Show cancelled results  
        for result in results["cancelled"]:
            print(f"\nJob {result.job_id} was cancelled: {result.error}")
    
    finally:
        # Clean up temporary files
        for file in invoice_files:
            file.unlink()
        os.rmdir(temp_dir)
        print(f"\nCleaned up temporary files in {temp_dir}")


if __name__ == "__main__":
    main()