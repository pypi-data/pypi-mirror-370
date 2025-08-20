import adss
import os
import pandas as pd
import argparse
import time
import threading
from queue import Queue

from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Pretty prints
from datetime import datetime

# Thread-safe printing
print_lock = threading.Lock()

def print_log(message, level="INFO"):
    if level == "ERROR":
        color = "\033[91m"  # Red color for error messages
    elif level == "WARNING":
        color = "\033[93m"  # Yellow color for warning messages
    elif level == "SUCCESS":
        color = "\033[92m"  # Green color for success messages
    else:
        color = "\033[94m"  # Blue color for info messages

    white_color = "\033[97m"  # White color for the timestamp
    reset_color = "\033[0m"   # Reset color

    with print_lock:
        print(f"{color}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level}] {white_color}{message}{reset_color}")

def print_field_status(field, status, details="", thread_id=None):
    if status == "STARTING":
        color = "\033[96m"  # Cyan
    elif status == "QUERYING":
        color = "\033[93m"  # Yellow
    elif status == "SAVING":
        color = "\033[95m"  # Magenta
    elif status == "COMPLETED":
        color = "\033[92m"  # Green
    elif status == "SKIPPED":
        color = "\033[90m"  # Gray
    elif status == "ERROR":
        color = "\033[91m"  # Red
    else:
        color = "\033[97m"  # White

    reset_color = "\033[0m"
    thread_info = f" [T{thread_id}]" if thread_id else ""
    
    with print_lock:
        print(f"{color}[{datetime.now().strftime('%H:%M:%S')}]{thread_info} {field}: {status}{reset_color} {details}")

print_log("Test")

# Fetch code
def main(multithreaded=False, fields_out_format='csv', max_workers=7):
    class Args:
        def __init__(self):
            self.username = 'splusdatateam'
            self.password = 'asdflkjh'
            self.outfolder = 'VAC_Catalogues/'

    args = Args()

    # Initialize client
    print_log("Initializing ADSS client...")
    client = adss.ADSSClient(
        base_url="https://andromeda.cbpf.br/", 
        username=args.username,
        password=args.password,
        verify_ssl=False
    )
    
    # Get database metadata
    print_log("Fetching database metadata...")
    metadata = client.get_database_metadata()
    print_log(f"Available schemas: {metadata.schema_names()}")
    
    schema = metadata.get_schema("splus")
    print_log(f"Available tables: {schema.table_names()}")
    
    table = schema.get_table("splus_idr6")
    print_log(f"Table columns: {len(table.column_names())} columns")
    
    # Get or load fields
    print_log("Loading or querying fields...")
    fields_file = os.path.join(args.outfolder, f"fields.csv")
    if not os.path.exists(fields_file):
        print_log("Querying distinct fields...")
        result = client.query_and_wait("SELECT DISTINCT field FROM splus.splus_idr6")
        print_log(f"Query result: {result}")
        
        os.makedirs(args.outfolder, exist_ok=True)
        result.to_csv(fields_file, index=False)
        fields = result.data["field"].tolist()
    else:
        fields = pd.read_csv(fields_file)["field"].tolist()
        print_log(f"Fields loaded from file: {len(fields)} fields")
    
    # Process each field
    print_log(f"Processing {len(fields)} fields...")
    splus_filters = ['u', 'j0378', 'j0395', 'j0410', 'j0430', 'g', 'j0515', 'r', 'j0660', 'i', 'j0861', 'z']
    apertures     = ['aper_3', 'aper_6', 'auto', 'auto_restricted', 'isophotal', 'petro', 'psf', 'pstotal']

    magnitudes = {}
    magnitude_errors = {}
    for aperture in apertures:
        magnitudes[aperture] = [f'mag_{aperture}_{f}' for f in splus_filters]
        if aperture != 'auto_restricted':
            magnitude_errors[aperture] = [f'err_mag_{aperture}_{f}' for f in splus_filters]

    columns_to_get = ['field', 'id', 'ra', 'dec', 'class_star_det', 'class_star_r', 
                      'flux_radius_as_20_det', 'flux_radius_as_50_det', 'flux_radius_as_70_det', 'flux_radius_as_90_det', 
                      'a_pixel_det', 'err_a_pixel_det', 'a_restricted_pixel_r', 'b_pixel_det', 'err_b_pixel_det', 'b_restricted_pixel_r', 
                      'ellipticity_det', 'elongation_det', 
                      'flags_det', 'flags_r', 
                      'fwhm_n_det', 'fwhm_pixels_det', 
                      'isophotal_area_pixel_det', 'kron_radius_det', 'kron_radius_restricted_r', 'petro_radius_det', 
                      'mu_background_r', 'mu_max_g', 'mu_max_r', 'mu_threshold_g', 'mu_threshold_r', 
                      's2n_aper_3_det', 's2n_aper_6_det', 's2n_auto_det', 's2n_iso_det', 's2n_petro_det', 's2n_psf_r', 's2n_pstotal_det']
    columns_to_get = (columns_to_get + magnitudes['aper_3'] + magnitudes['aper_6'] + magnitudes['auto'] + magnitudes['auto_restricted'] + 
                      magnitudes['isophotal'] + magnitudes['petro'] + magnitudes['psf'] + magnitudes['pstotal'])
    columns_to_get = (columns_to_get + magnitude_errors['aper_3'] + magnitude_errors['aper_6'] + magnitude_errors['auto'] + 
                      magnitude_errors['isophotal'] + magnitude_errors['petro'] + magnitude_errors['psf'] + magnitude_errors['pstotal'])

    print_log(f"Columns to get: {len(columns_to_get)} columns")
    print_log(f"Files will be saved in: {args.outfolder}")
    print_log(f"Using {max_workers} parallel workers")

    if not multithreaded:
        os.makedirs(args.outfolder, exist_ok=True)
        pbar = tqdm(enumerate(fields, 1), total=len(fields))
        for i, field in pbar:
            field_file = os.path.join(args.outfolder, f"{field}.{fields_out_format}")
            if os.path.exists(field_file):
                print(f"[{i}/{len(fields)}] Skipping {field} (already exists)")
                continue
            
            pbar.set_description_str(f"Processing field: {field}")
            try:
                result = client.query_and_wait(
                    f"""SELECT {', '.join(columns_to_get)} 
                        FROM splus.splus_idr6 
                        WHERE field = '{field}'"""
                )
                
                if result.data.empty:
                    print(f"  No data found for field: {field}")
                else:
                    if fields_out_format == 'parquet':
                        result.to_parquet(field_file, index=False)
                    if fields_out_format == 'csv':
                        result.to_csv(field_file, index=False)
            except Exception as e:
                print(f"  Error processing field {field}: {e}")

    else:
        print_log("Starting multithreaded processing with detailed progress tracking...")
        print()
        
        os.makedirs(args.outfolder, exist_ok=True)
        
        # Statistics tracking
        completed_count = 0
        skipped_count = 0
        error_count = 0
        stats_lock = threading.Lock()
        
        def update_stats(status):
            nonlocal completed_count, skipped_count, error_count
            with stats_lock:
                if status == "COMPLETED":
                    completed_count += 1
                elif status == "SKIPPED":
                    skipped_count += 1
                elif status == "ERROR":
                    error_count += 1

        def process_field(field, field_index, total_fields):
            thread_id = threading.current_thread().ident % 1000  # Short thread ID
            
            field_file = os.path.join(args.outfolder, f"{field}.{fields_out_format}")
            
            # Check if file already exists
            if os.path.exists(field_file):
                print_field_status(field, "SKIPPED", "file already exists", thread_id)
                update_stats("SKIPPED")
                return {"field": field, "status": "skipped", "thread_id": thread_id}

            try:
                print_field_status(field, "STARTING", f"[{field_index}/{total_fields}]", thread_id)
                
                # Query phase
                print_field_status(field, "QUERYING", "executing database query...", thread_id)
                start_time = time.time()
                
                result = client.query_and_wait(
                    f"""SELECT {', '.join(columns_to_get)}
                        FROM splus.splus_idr6 
                        WHERE field = '{field}'"""
                )
                print_field_status(field, "FINISHED", "executing database query...", thread_id)
                
                query_time = time.time() - start_time
                
                if result.data.empty:
                    print_field_status(field, "COMPLETED", f"no data found (query: {query_time:.1f}s)", thread_id)
                    update_stats("COMPLETED")
                    return {"field": field, "status": "no_data", "query_time": query_time, "thread_id": thread_id}
                
                # Save phase
                row_count = len(result.data)
                print_field_status(field, "SAVING", f"{row_count:,} rows (query: {query_time:.1f}s)", thread_id)
                
                save_start = time.time()
                if fields_out_format == 'parquet':
                    result.to_parquet(field_file, index=False)
                elif fields_out_format == 'csv':
                    result.to_csv(field_file, index=False)
                
                save_time = time.time() - save_start
                total_time = time.time() - start_time
                
                print_field_status(field, "COMPLETED", 
                                 f"{row_count:,} rows saved (query: {query_time:.1f}s, save: {save_time:.1f}s, total: {total_time:.1f}s)", 
                                 thread_id)
                
                update_stats("COMPLETED")
                return {
                    "field": field, 
                    "status": "success", 
                    "rows": row_count,
                    "query_time": query_time,
                    "save_time": save_time,
                    "total_time": total_time,
                    "thread_id": thread_id
                }
                
            except Exception as e:
                print_field_status(field, "ERROR", f"{str(e)}", thread_id)
                update_stats("ERROR")
                return {"field": field, "status": "error", "error": str(e), "thread_id": thread_id}

        # Submit all jobs
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all futures
            future_to_field = {}
            for i, field in enumerate(fields, 1):
                future = executor.submit(process_field, field, i, len(fields))
                future_to_field[future] = field
            
            # Process completed futures with progress bar
            with tqdm(total=len(fields), desc="Overall Progress", 
                     bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
                
                for future in as_completed(future_to_field):
                    try:
                        result = future.result()
                        results.append(result)
                        
                        # Update progress bar with current stats
                        pbar.set_postfix({
                            'completed': completed_count,
                            'skipped': skipped_count, 
                            'errors': error_count
                        })
                        pbar.update(1)
                        
                    except Exception as e:
                        field = future_to_field[future]
                        print_field_status(field, "ERROR", f"Future exception: {str(e)}")
                        results.append({"field": field, "status": "future_error", "error": str(e)})
                        pbar.update(1)

        # Summary
        print()
        print_log("=" * 60, "INFO")
        print_log("PROCESSING SUMMARY", "INFO")
        print_log("=" * 60, "INFO")
        print_log(f"Total fields: {len(fields)}")
        print_log(f"Completed: {completed_count}", "SUCCESS")
        print_log(f"Skipped: {skipped_count}", "WARNING")
        print_log(f"Errors: {error_count}", "ERROR")
        
        # Show errors if any
        if error_count > 0:
            print_log("Fields with errors:", "ERROR")
            for result in results:
                if result.get("status") in ["error", "future_error"]:
                    print_log(f"  {result['field']}: {result.get('error', 'Unknown error')}", "ERROR")

# Run code
if __name__ == "__main__":
    main(multithreaded=True, fields_out_format='parquet', max_workers=7)