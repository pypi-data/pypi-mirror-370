from typing import Annotated

import os
import typer
import logging
import pandas as pd

from pathlib import Path

from .utils import (
    Engine,
    ContoursExtension,
    PatchExtension,
    PatchMode,
    load_config_file,
    update_tracking_df,
    extract_contours_from_slide,
    extract_patches_from_slide,
)

log = logging.getLogger(__name__)

app_preprocessing = typer.Typer(
    name="PrismToolBox Preprocessing CLI",
    help="A CLI for preprocessing WSIs using the PrismToolBox.",
    no_args_is_help=True,
    add_completion=True,
    rich_markup_mode="rich")
        
@app_preprocessing.command(no_args_is_help=True)
def contour(
    ctx: typer.Context,
    slide_directory: Annotated[str, typer.Argument(
        help="Path to the directory containing the files.")],
    results_directory: Annotated[str, typer.Argument(
        help="Path to the directory where the results will be saved.")],
    engine: Annotated[Engine, typer.Option(
        help="Engine to use for reading the slides.",
        case_sensitive=False)] = Engine.openslide,
    annotations_directory: Annotated[str | None, typer.Option(
        help="Path to the directory containing the annotations."
    )] = None,
    contour_exts: Annotated[list[ContoursExtension], typer.Option(
        help="File extensions for the contours annotations.",
        case_sensitive=False,
    )] = [ContoursExtension.pickle],
    config_file: Annotated[str | None, typer.Option(
        help="Path to the configuration file for tissue extraction."
    )] = None,
    visualize: Annotated[bool, typer.Option(
        help="Visualize the contours extracted.",
    )] = False,
):
    """Extract tissue contours from the slides in a specified directory."""
    
    # Set default parameters
    params_detect_tissue = {
        "seg_level": 4,
        "window_avg": 30,
        "window_eng": 5,
        "thresh": 190,
        "area_min": 5e4,
    }
    
    params_visualize_WSI = {
        "vis_level": 4,
        "number_contours": False,
        "line_thickness": 50,
    }
    
    if config_file is None or not os.path.exists(config_file):
        log.info(f"Using default parameters for tissue extraction.")
    else:
        log.info(f"Using parameters from config file: {config_file}")
        # Load parameters from config file
        params_detect_tissue = load_config_file(config_file, 
                                                dict_to_update=params_detect_tissue,
                                                key_to_check='contour_settings')
        if visualize:
            params_visualize_WSI = load_config_file(config_file,
                                                dict_to_update=params_visualize_WSI,
                                                key_to_check='visualization_settings')
        
    directory_contours = os.path.join(results_directory, f"contours")    
    Path(directory_contours).mkdir(parents=True, exist_ok=True)
    
    if visualize:
        directory_visualize = os.path.join(results_directory, f"contoured_images")
        Path(directory_visualize).mkdir(parents=True, exist_ok=True)

    if ctx.obj.get("tracking_file", True):
        # Create an empty tracking file to keep track of the processing status
        tracking_file_path = os.path.join(results_directory, "tracking_contouring.csv")
        if not os.path.exists(tracking_file_path):
            # Create the tracking file if it does not exist
            col_names = ["file_name", "nb contours"] + list(params_detect_tissue.keys()) + ["status", "error message", "timestamp"]
            tracking_df = pd.DataFrame(columns=col_names)
            tracking_df.to_csv(tracking_file_path, index=False)
            
    # Iterate over the files in the directory
    for file_name in os.listdir(slide_directory):
        slide_path = os.path.join(slide_directory, file_name)
        try:
            already_processed, nb_contours = extract_contours_from_slide(
                slide_path,
                engine,
                directory_contours,
                params_detect_tissue,
                contour_exts,
                annotations_directory,
                visualize,
                directory_visualize,
                params_visualize_WSI,
                ctx.obj["skip_existing"]
            )
            if ctx.obj.get("tracking_file", True):
                # Update the tracking file with the processing status
                update_tracking_df(
                    tracking_file_path,
                    file_name,
                    ("contours", nb_contours),
                    params_dict=params_detect_tissue,
                    already_processed=already_processed,
                )
        except Exception as e:
            if ctx.obj.get("tracking_file", True):
                # Update the tracking file with the processing status
                update_tracking_df(
                    tracking_file_path,
                    file_name,
                    nb_objects=("contours", 0),
                    params_dict=params_detect_tissue,
                    error_message=str(e)
                )
            if ctx.obj.get("skip_errors", True):
                log.warning(f"Skipping slide {file_name}: {e}")
                continue
            else:
                log.error(f"Error processing slide {file_name}:")
                raise
       
    print("Contours extracted and saved successfully.")
    
@app_preprocessing.command(no_args_is_help=True)
def patchify(
    ctx: typer.Context,
    slide_directory: Annotated[str, typer.Argument(
        help="Path to the directory containing the files.")],
    results_directory: Annotated[str, typer.Argument(
        help="Path to the directory where the results will be saved.")],
    roi_csv: Annotated[str | None, typer.Option(
        help="Path to the file containing the ROI coordinates."
    )] = None,
    contours_directory: Annotated[str | None, typer.Option(
        help="Path to the directory containing the contours annotations."
    )] = None,
    engine: Annotated[Engine, typer.Option(
        help="Engine to use for reading the slides.",
        case_sensitive=False)] = Engine.openslide,
    patch_exts: Annotated[list[PatchExtension], typer.Option(
        help="File extensions for the patches.",
        case_sensitive=False,
    )] = [PatchExtension.h5],
    mode: Annotated[PatchMode, typer.Option(
        help="The mode to use for patch extraction. Possible values are 'contours', 'roi', and 'all'.",
        case_sensitive=False,
    )] = PatchMode.all,
    config_file: Annotated[str | None, typer.Option(
        help="Path to the configuration file for patch extraction."
    )] = None,
    stitch: Annotated[bool, typer.Option(
        help="Whether to stitch the extracted patches into a single image for visualization.",
    )] = True,
    force_patch_extraction: Annotated[bool, typer.Option(
        help="Force patch extraction using mode 'all', even if no contours were detected when"
        "using 'contours' mode (useful if problem to extract contours on some slides).",
    )] = False,
    num_workers: Annotated[int, typer.Option(
        help="Number of workers to use for parallel processing.",
        min=1,
    )] = 10,
):
    """Extract patches from the slides in a specified directory."""
    # Set default parameters
    params_patches = {"patch_size": 256, "patch_level": 0, "overlap": 0,
                      "units": ["px", "px"], "contours_mode": "four_pt", "rgb_threshs": [2, 240], 
                      "percentages": [0.6, 0.9]}
    params_stitch_WSI = {"vis_level": 4, "draw_grid": False}
    
    if config_file is None or not os.path.exists(config_file):
        log.info(f"Using default parameters for tissue extraction.")
    else:
        log.info(f"Using parameters from config file: {config_file}")
        # Load parameters from config file
        params_patches = load_config_file(config_file, 
                                          dict_to_update=params_patches,
                                          key_to_check='patch_settings')
        if stitch:
            params_stitch_WSI = load_config_file(config_file,
                                                 dict_to_update=params_stitch_WSI,
                                                 key_to_check='stitching_settings')
    params_patches = {**{"mode": mode}, **params_patches}
    # Path to the directory where the patches will be saved
    directory_patches = os.path.join(results_directory,
                                     f"patches_{params_patches['patch_size']}_overlap"
                                     f"_{params_patches['overlap']}")
    Path(directory_patches).mkdir(parents=True, exist_ok=True)
    
    if stitch:
        # Path to the directory where the stitched images will be saved
        directory_stitch = os.path.join(results_directory,
                                        f"stitched_images_{params_patches['patch_size']}_overlap"
                                        f"_{params_patches['overlap']}")
        Path(directory_stitch).mkdir(parents=True, exist_ok=True)
    
    if ctx.obj.get("tracking_file", True):
        # Create an empty tracking file to keep track of the processing status
        tracking_file_path = os.path.join(results_directory, "tracking_patching.csv")
        if not os.path.exists(tracking_file_path):
            # Create the tracking file if it does not exist
            col_names = ["file_name", "nb patches"] + list(params_patches.keys()) + ["status", "error message", "timestamp"]
            tracking_df = pd.DataFrame(columns=col_names)
            tracking_df.to_csv(tracking_file_path, index=False)
            
    # Iterate over the files in the directory
    for file_name in os.listdir(slide_directory):
        slide_path = os.path.join(slide_directory, file_name)
        try:
            already_processed, nb_patches = extract_patches_from_slide(
                slide_path,
                engine,
                directory_patches,
                params_patches,
                patch_exts,
                roi_csv,
                contours_directory,
                stitch,
                directory_stitch,
                params_stitch_WSI,
                force_patch_extraction,
                ctx.obj["skip_existing"],
                num_workers=num_workers
            )
            if ctx.obj.get("tracking_file", True):
                # Update the tracking file with the processing status
                update_tracking_df(
                    tracking_file_path,
                    file_name,
                    ("patches", nb_patches),
                    params_dict=params_patches,
                    already_processed=already_processed
                )
        except Exception as e:
            if ctx.obj.get("tracking_file", True):
                # Update the tracking file with the processing status
                update_tracking_df(
                    tracking_file_path,
                    file_name,
                    ("patches", 0),
                    params_dict=params_patches,
                    error_message=str(e)
                )
            if ctx.obj.get("skip_errors", True):
                log.warning(f"Skipping slide {file_name}: {e}")
                continue
            else:
                log.error(f"Error processing slide {file_name}:")
                raise
        if params_patches["mode"] != mode:
            log.warning(f"Mode {params_patches['mode']} was used for patch extraction instead of {mode}." \
                "Reverting back to mode {mode} for the next slide.")
            params_patches["mode"] = mode
    print("Patches extracted and saved successfully.")