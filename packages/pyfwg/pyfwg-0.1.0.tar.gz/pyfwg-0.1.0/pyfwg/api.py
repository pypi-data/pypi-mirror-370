# pyfwg/api.py

import os
import shutil
import logging
import subprocess
import time
from typing import List, Union, Optional, Dict, Any

# Import the workflow class to use it as an internal engine
from .workflow import MorphingWorkflow


def _robust_rmtree(path: str, max_retries: int = 5, delay: float = 0.5):
    """
    A robust version of shutil.rmtree that retries on PermissionError.
    This is useful for handling filesystem race conditions on Windows.
    """
    for i in range(max_retries):
        try:
            shutil.rmtree(path)
            return
        except PermissionError:
            logging.warning(f"PermissionError deleting {path}. Retrying in {delay}s... (Attempt {i + 1}/{max_retries})")
            time.sleep(delay)
    logging.error(f"Failed to delete directory {path} after {max_retries} retries.")


def morph_epw(*,
              epw_paths: Union[str, List[str]],
              fwg_jar_path: str,
              output_dir: str = './morphed_epws',
              delete_temp_files: bool = True,
              temp_base_dir: str = './morphing_temp_results',
              fwg_show_tool_output: bool = False,
              fwg_params: Optional[Dict[str, Any]] = None,
              # --- Explicit FutureWeatherGenerator Arguments ---
              fwg_gcms: Optional[List[str]] = None, fwg_create_ensemble: bool = True,
              fwg_winter_sd_shift: float = 0.0, fwg_summer_sd_shift: float = 0.0,
              fwg_month_transition_hours: int = 72, fwg_use_multithreading: bool = True,
              fwg_interpolation_method_id: int = 0, fwg_limit_variables: bool = True,
              fwg_solar_hour_adjustment: int = 1, fwg_diffuse_irradiation_model: int = 1,
              fwg_add_uhi: bool = True, fwg_epw_original_lcz: int = 14, fwg_target_uhi_lcz: int = 1):
    """Performs a direct, one-shot morphing of EPW files with full parameter control.

    This function provides a simple interface to the morphing process while
    still allowing full customization of the FutureWeatherGenerator tool. It
    validates all parameters before execution and runs the entire workflow in
    a single call.

    The generated .epw and .stat files are saved directly to the output
    directory using the default filenames produced by the FWG tool.

    Args:
        epw_paths (Union[str, List[str]]): A single path or a list of paths
            to the EPW files to be processed.
        fwg_jar_path (str): Path to the `FutureWeatherGenerator.jar` file.
        output_dir (str, optional): Directory where the final morphed files
            will be saved. Defaults to './morphed_epws'.
        delete_temp_files (bool, optional): If True, temporary folders are
            deleted after processing. Defaults to True.
        temp_base_dir (str, optional): Base directory for temporary files.
            Defaults to './morphing_temp_results'.
        fwg_show_tool_output (bool, optional): If True, prints the FWG tool's
            console output in real-time. Defaults to False.
        fwg_params (Optional[Dict[str, Any]], optional): A dictionary for base
            FWG parameters. Any explicit `fwg_` argument will override this.
            Defaults to None.

        (All other `fwg_` arguments are explained in the MorphingWorkflow class)

    Returns:
        List[str]: A list of absolute paths to the successfully created .epw
                   and .stat files.

    Raises:
        ValueError: If the provided FWG parameters fail validation.
    """
    logging.info("--- Starting Direct Morphing Process ---")

    # --- 1. Use the MorphingWorkflow class internally ---
    workflow = MorphingWorkflow()

    # Normalize the input to always be a list.
    epw_files = [epw_paths] if isinstance(epw_paths, str) else epw_paths

    # Manually populate the epw_categories attribute. This is the step that
    # map_categories() would normally perform. For this simple function, we
    # just need the file paths, with no complex categories.
    workflow.epw_categories = {
        os.path.abspath(path): {} for path in epw_files if os.path.exists(path)
    }

    # --- 2. Configure and Validate ---
    # Call set_morphing_config to reuse all validation and parameter-building logic.
    workflow.set_morphing_config(
        fwg_jar_path=fwg_jar_path,
        delete_temp_files=delete_temp_files,
        temp_base_dir=temp_base_dir,
        fwg_show_tool_output=fwg_show_tool_output,
        fwg_params=fwg_params,
        fwg_gcms=fwg_gcms, fwg_create_ensemble=fwg_create_ensemble,
        fwg_winter_sd_shift=fwg_winter_sd_shift, fwg_summer_sd_shift=fwg_summer_sd_shift,
        fwg_month_transition_hours=fwg_month_transition_hours, fwg_use_multithreading=fwg_use_multithreading,
        fwg_interpolation_method_id=fwg_interpolation_method_id, fwg_limit_variables=fwg_limit_variables,
        fwg_solar_hour_adjustment=fwg_solar_hour_adjustment, fwg_diffuse_irradiation_model=fwg_diffuse_irradiation_model,
        fwg_add_uhi=fwg_add_uhi, fwg_epw_original_lcz=fwg_epw_original_lcz, fwg_target_uhi_lcz=fwg_target_uhi_lcz
    )

    # Stop execution if validation failed.
    if not workflow.is_config_valid:
        raise ValueError("FWG parameter validation failed. Please check the warnings in the log above.")

    # --- 3. Execute the Morphing for each file ---
    os.makedirs(output_dir, exist_ok=True)
    final_file_paths = []

    # Use the now-correctly-populated list of files to be morphed.
    for epw_path in workflow.epws_to_be_morphed:
        temp_epw_output_dir = os.path.join(workflow.inputs['temp_base_dir'], os.path.splitext(os.path.basename(epw_path))[0])
        os.makedirs(temp_epw_output_dir, exist_ok=True)

        # Reuse the low-level execution method from the class.
        success = workflow._execute_single_morph(epw_path, temp_epw_output_dir)

        if success:
            # Move the resulting .epw and .stat files to the final output directory.
            for generated_file in os.listdir(temp_epw_output_dir):
                if generated_file.endswith((".epw", ".stat")):
                    source_path = os.path.join(temp_epw_output_dir, generated_file)
                    dest_path = os.path.join(output_dir, generated_file)
                    shutil.move(source_path, dest_path)
                    final_file_paths.append(os.path.abspath(dest_path))

            # Clean up the temporary directory if requested.
            if workflow.inputs['delete_temp_files']:
                _robust_rmtree(temp_epw_output_dir)

    logging.info(f"Direct morphing complete. {len(final_file_paths)} files created in {os.path.abspath(output_dir)}")
    return final_file_paths