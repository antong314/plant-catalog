#!/usr/bin/env python3
"""
Tropical Plants Image Generator

This script reads the tropical-plants.csv file and generates botanical illustrations
for each plant using the NanoBanana API.

Usage:
    export NANOBANANA_API_KEY="your_api_key_here"
    python generate_images.py

Options:
    --start N       Start from row N (0-indexed, skip header)
    --limit N       Only process N images
    --dry-run       Print prompts without making API calls
    --verbose       Enable verbose logging
"""

import csv
import os
import sys
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global verbose flag
VERBOSE = False


def log(message: str, level: str = "INFO"):
    """Print a timestamped log message."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}", flush=True)


def log_verbose(message: str):
    """Print a verbose log message (only if verbose mode is enabled)."""
    if VERBOSE:
        log(message, "DEBUG")

# Configuration
API_BASE_URL = "https://api.nanobananaapi.ai/api/v1"
GENERATE_ENDPOINT = f"{API_BASE_URL}/nanobanana/generate-pro"
TASK_ENDPOINT = f"{API_BASE_URL}/nanobanana/record-info"  # GET /record-info?taskId=xxx

# Polling configuration
POLL_INTERVAL = 5  # seconds between status checks
MAX_POLL_TIME = 600  # maximum time to wait for a single image (10 minutes)

# Image settings
RESOLUTION = "1K"
ASPECT_RATIO = "1:1"


def get_api_key():
    """Get API key from environment variable."""
    api_key = os.environ.get("NANOBANANA_API_KEY")
    if not api_key:
        print("Error: NANOBANANA_API_KEY environment variable not set.")
        print("Please set it with: export NANOBANANA_API_KEY='your_key_here'")
        sys.exit(1)
    return api_key


def submit_generation_task(api_key: str, prompt: str) -> str:
    """
    Submit an image generation task to the NanoBanana API.
    
    Returns the task ID.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "resolution": RESOLUTION,
        "aspectRatio": ASPECT_RATIO
    }
    
    log_verbose(f"POST {GENERATE_ENDPOINT}")
    log_verbose(f"Payload: resolution={RESOLUTION}, aspectRatio={ASPECT_RATIO}")
    log_verbose(f"Prompt (first 150 chars): {prompt[:150]}...")
    
    response = requests.post(GENERATE_ENDPOINT, headers=headers, json=payload)
    
    log_verbose(f"Response status: {response.status_code}")
    response.raise_for_status()
    
    data = response.json()
    log_verbose(f"Response body: {data}")
    
    if data.get("code") != 200:
        raise Exception(f"API error: {data.get('message', 'Unknown error')}")
    
    task_id = data.get("data", {}).get("taskId")
    if not task_id:
        raise Exception("No taskId in response")
    
    return task_id


def poll_task_status(api_key: str, task_id: str) -> dict:
    """
    Poll the task status until completion or timeout.
    
    Returns the completed task data including the image URL.
    
    successFlag values:
        0: GENERATING
        1: SUCCESS
        2: CREATE_TASK_FAILED
        3: GENERATE_FAILED
    """
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    start_time = time.time()
    poll_count = 0
    
    while True:
        poll_count += 1
        elapsed = time.time() - start_time
        if elapsed > MAX_POLL_TIME:
            raise TimeoutError(f"Task {task_id} timed out after {MAX_POLL_TIME} seconds")
        
        log_verbose(f"Poll #{poll_count}: GET {TASK_ENDPOINT}?taskId={task_id}")
        response = requests.get(TASK_ENDPOINT, headers=headers, params={"taskId": task_id})
        log_verbose(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        data = response.json()
        task_data = data.get("data", {})
        success_flag = task_data.get("successFlag")
        
        status_names = {0: "GENERATING", 1: "SUCCESS", 2: "CREATE_FAILED", 3: "GENERATE_FAILED"}
        status_name = status_names.get(success_flag, f"UNKNOWN({success_flag})")
        
        if success_flag == 1:  # SUCCESS
            log(f"Generation complete! (took {int(elapsed)}s, {poll_count} polls)")
            log_verbose(f"Task response: {task_data}")
            return task_data
        elif success_flag == 2:  # CREATE_TASK_FAILED
            error_msg = task_data.get("errorMessage", "Task creation failed")
            raise Exception(f"Task creation failed: {error_msg}")
        elif success_flag == 3:  # GENERATE_FAILED
            error_msg = task_data.get("errorMessage", "Generation failed")
            raise Exception(f"Generation failed: {error_msg}")
        
        # Still generating (successFlag == 0), wait and retry
        log(f"Status: {status_name} | Elapsed: {int(elapsed)}s | Poll #{poll_count}")
        time.sleep(POLL_INTERVAL)


def download_image(url: str, output_path: Path) -> int:
    """Download an image from URL and save to the specified path. Returns file size in bytes."""
    log_verbose(f"Downloading from: {url}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_bytes = 0
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            total_bytes += len(chunk)
    
    return total_bytes


def process_plant(api_key: str, image_name: str, prompt: str, output_dir: Path, dry_run: bool = False) -> bool:
    """
    Process a single plant: generate image and save it.
    
    Returns True if successful, False otherwise.
    """
    output_path = output_dir / image_name
    
    # Skip if image already exists
    if output_path.exists():
        log(f"SKIP: {image_name} (already exists)")
        return True
    
    if dry_run:
        log(f"[DRY RUN] Would generate: {image_name}")
        log_verbose(f"Prompt: {prompt[:200]}...")
        return True
    
    try:
        # Submit generation task
        log(f"Submitting task for: {image_name}")
        task_id = submit_generation_task(api_key, prompt)
        log(f"Task submitted: {task_id}")
        
        # Poll for completion
        log(f"Polling for completion...")
        task_data = poll_task_status(api_key, task_id)
        
        # Get image URL from completed task (in response.resultImageUrl)
        response_data = task_data.get("response", {})
        image_url = response_data.get("resultImageUrl")
        
        if not image_url:
            raise Exception(f"No resultImageUrl in response: {task_data}")
        
        log_verbose(f"Image URL: {image_url}")
        
        # Download and save image
        log(f"Downloading image...")
        file_size = download_image(image_url, output_path)
        file_size_kb = file_size / 1024
        log(f"SAVED: {output_path.name} ({file_size_kb:.1f} KB)")
        
        return True
        
    except Exception as e:
        log(f"ERROR: {e}", "ERROR")
        return False


def main():
    global VERBOSE
    
    parser = argparse.ArgumentParser(description="Generate botanical illustrations from CSV")
    parser.add_argument("--start", type=int, default=0, help="Start from row N (0-indexed)")
    parser.add_argument("--limit", type=int, default=None, help="Only process N images")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without making API calls")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    
    VERBOSE = args.verbose
    
    # Setup paths
    script_dir = Path(__file__).parent
    csv_path = script_dir / "tropical-plants.csv"
    output_dir = script_dir / "img"
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    # Get API key (unless dry run)
    api_key = None
    if not args.dry_run:
        api_key = get_api_key()
    
    # Print configuration
    print("=" * 60, flush=True)
    print("TROPICAL PLANTS IMAGE GENERATOR", flush=True)
    print("=" * 60, flush=True)
    log(f"CSV file: {csv_path}")
    log(f"Output directory: {output_dir}")
    log(f"Resolution: {RESOLUTION}")
    log(f"Aspect Ratio: {ASPECT_RATIO}")
    log(f"Start row: {args.start}")
    log(f"Limit: {args.limit if args.limit else 'None (all rows)'}")
    log(f"Dry run: {args.dry_run}")
    log(f"Verbose: {VERBOSE}")
    log(f"API endpoint: {GENERATE_ENDPOINT}")
    print("-" * 60, flush=True)
    
    success_count = 0
    error_count = 0
    skip_count = 0
    start_time = time.time()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)  # Load all rows to get total count
        total_rows = len(rows)
        
        log(f"Total plants in CSV: {total_rows}")
        print("-" * 60, flush=True)
        
        for i, row in enumerate(rows):
            # Skip rows before start
            if i < args.start:
                continue
            
            # Stop if limit reached
            if args.limit and (i - args.start) >= args.limit:
                break
            
            image_name = row.get("Image Name", "").strip()
            prompt = row.get("Image Prompt", "").strip()
            english_name = row.get("English Name", "").strip()
            botanical_name = row.get("Botanical Name", "").strip()
            
            if not image_name or not prompt:
                log(f"[{i+1}/{total_rows}] SKIP: Row {i} - missing image name or prompt", "WARN")
                skip_count += 1
                continue
            
            print(flush=True)
            log(f"[{i+1}/{total_rows}] {english_name} ({botanical_name})")
            
            # Check if already exists
            if (output_dir / image_name).exists():
                log(f"SKIP: {image_name} (already exists)")
                skip_count += 1
                continue
            
            success = process_plant(api_key, image_name, prompt, output_dir, args.dry_run)
            
            if success:
                success_count += 1
            else:
                error_count += 1
                # Optional: add delay after errors to avoid rate limiting
                time.sleep(2)
            
            # Progress summary
            processed = success_count + error_count + skip_count
            elapsed = time.time() - start_time
            avg_time = elapsed / max(success_count, 1)
            log(f"Progress: {processed} processed | {success_count} success | {error_count} errors | {skip_count} skipped")
            if success_count > 0:
                log(f"Average time per image: {avg_time:.1f}s")
            
            # Add a small delay between requests to be nice to the API
            if not args.dry_run and success:
                time.sleep(1)
    
    # Final summary
    total_time = time.time() - start_time
    print(flush=True)
    print("=" * 60, flush=True)
    log("COMPLETE")
    print("=" * 60, flush=True)
    log(f"Successful: {success_count}")
    log(f"Errors: {error_count}")
    log(f"Skipped: {skip_count}")
    log(f"Total processed: {success_count + error_count + skip_count}")
    log(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")


if __name__ == "__main__":
    main()
