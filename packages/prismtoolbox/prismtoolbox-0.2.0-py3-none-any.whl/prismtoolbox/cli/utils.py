from typing import Any

import os
import yaml
import logging
import pandas as pd
from enum import Enum

log = logging.getLogger(__name__)

CONTOUR_EXTS_MAP = {"pickle": "pkl", "geojson": "geojson"}
PATCH_EXTS_MAP = {"h5": "h5", "geojson": "geojson"}

class Engine(str, Enum):
    openslide = "openslide"
    tiffslide = "tiffslide"
    
class ContoursExtension(str, Enum):
    geojson = "geojson"
    pickle = "pickle"
    
class PatchExtension(str, Enum):
    h5 = "h5"
    geojson = "geojson"
    
class PatchMode(str, Enum):
    contours = "contours"
    roi = "roi"
    all = "all"

def load_config_file(config_file: str,
                     dict_to_update: dict[str, Any],
                     key_to_check: str,
                     ) -> dict[str, Any]:
    """Load configuration from a YAML file.

    Args:
        config_file (str, optional): Path to the configuration file. If not provided, it will look for a default config file.
        dict_to_update (dict[str, Any], optional): Dictionary to update with parameters from the config file. Defaults to None.
        key_to_check (str, optional): Key to check in the config file. If this key is not found, an error will be raised. Defaults to None.

    Returns:
        dict[str, Any]: The updated dictionary with parameters from the config file.
    """
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update parameters from the config file
        if key_to_check in config:
            custom_config = config.get(key_to_check, {})
            print(f"Custom config for {key_to_check}: {custom_config}")
            if all(k in custom_config for k in dict_to_update.keys()):
                dict_to_update.update(custom_config)
                log.info(f"Loaded {key_to_check} parameters from config file")
            else:
                log.error(f"Incomplete {key_to_check} parameters in config file")
                exit("Please check the config file for missing parameters.")
        else:
            log.error(f"{key_to_check} not found in config file")
            exit(f"Please check the config file for the {key_to_check} section.")
    else:
        log.error(f"Config file {config_file} does not exist.")
        exit(f"Please provide a valid config file at {config_file}.")
        
    return dict_to_update

def update_tracking_df(
    tracking_file_path: str,
    file_name: str,
    nb_objects: tuple[str, int],
    params_dict: dict[str, Any],
    already_processed: bool = False,
    error_message: str = ""
) -> None:
    """
    Update the tracking DataFrame with the processing status.
    """
    tracking_df = pd.read_csv(tracking_file_path)
    if already_processed and file_name in tracking_df["file_name"].values:
        # If the file is already processed, update the status
        tracking_df.loc[tracking_df["file_name"] == file_name, "status"] = "already_processed"
    else:
        # If the file is not in the tracking DataFrame, create a new row
        timestamp = pd.Timestamp.now()
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        if error_message != "":
            status = "not_processed"
        else:
            status = "processed" if not already_processed else "already_processed"
        if status != "processed":
            params_dict = {k: "" for k in params_dict.keys()}
        new_row = {
            "file_name": file_name,
            f"nb {nb_objects[0]}": str(nb_objects[1]),
            **params_dict,
            "status": status,
            "error message": error_message,
            "timestamp": timestamp
        }
        tracking_df = pd.concat([tracking_df, pd.DataFrame([new_row])], ignore_index=True)
    tracking_df.to_csv(tracking_file_path, index=False)
    
def extract_contours_from_slide(
    slide_path: str,
    engine: Engine,
    directory_contours:str,
    params_detect_tissue: dict[str, Any],
    contour_exts: list[ContoursExtension],
    annotations_directory: None | str,
    visualize: bool,
    directory_visualize: str | None,
    params_visualize_WSI: dict[str, Any] | None,
    skip_existing: bool = True,
) -> tuple[bool, int]:
    import prismtoolbox as ptb
    # Load the image
    WSI_object = ptb.WSI(slide_path, engine=engine)
    already_processed = False
    if skip_existing and \
        all([os.path.exists(os.path.join(directory_contours, f"{WSI_object.slide_name}.{CONTOUR_EXTS_MAP[ext]}")) for ext in contour_exts]):
            log.warning(f"Contours already extracted for {WSI_object.slide_name}, skipping.")
            already_processed = True
            WSI_object.load_tissue_contours(os.path.join(directory_contours, f"{WSI_object.slide_name}.{CONTOUR_EXTS_MAP[contour_exts[0]]}"))
            # Check if the contours are empty
            if WSI_object.tissue_contours is None:
                raise RuntimeError(f"Found a contour file for {WSI_object.slide_name}, but loading did not changed WSI_object.tissue_contours. " \
                                   "Please check the file.")
            else:
                return already_processed, len(WSI_object.tissue_contours)
    print(f"Processing {WSI_object.slide_name}...")
    # Extract the contours from the image
    WSI_object.detect_tissue(**params_detect_tissue)
    # Check if the contours are empty
    if WSI_object.tissue_contours is None:
            raise RuntimeError(f"detect_tissue for {WSI_object.slide_name} did not change WSI_object.tissue_contours.")
    # Apply pathologist annotations
    if annotations_directory is not None:
        WSI_object.apply_pathologist_annotations(os.path.join(annotations_directory, f"{WSI_object.slide_name}.geojson"))
    # Save extracted contours
    for contours_ext in contour_exts:
        WSI_object.save_tissue_contours(directory_contours, file_format=contours_ext)
    if visualize:
        # Visualize the extracted contours on the tissue
        if params_visualize_WSI is None or directory_visualize is None:
            raise ValueError("Parameters for visualization or directory for saving visualizations are not provided.")
        img = WSI_object.visualize(**params_visualize_WSI)
        img.save(os.path.join(directory_visualize, f"{WSI_object.slide_name}.jpg"))
    return already_processed, len(WSI_object.tissue_contours)

def extract_patches_from_slide(
    slide_path: str,
    engine: Engine,
    directory_patches: str,
    params_patches: dict[str, Any],
    patch_exts: list[PatchExtension],
    roi_csv: None | str,
    contours_directory: None | str,
    stitch: bool,
    directory_stitch: str | None,
    params_stitch_WSI: dict[str, Any] | None,
    force_patch_extraction: bool = False,
    skip_existing: bool = True,
    num_workers: int = 10
) -> tuple[bool, int]:
    import prismtoolbox as ptb
    # Load the image
    WSI_object = ptb.WSI(slide_path, engine=engine)
    print(f"Processing {WSI_object.slide_name}...")
    already_processed = False
    if skip_existing and \
        all([os.path.exists(os.path.join(directory_patches, f"{WSI_object.slide_name}.{PATCH_EXTS_MAP[ext]}")) for ext in patch_exts]):
            log.warning(f"Patches already extracted for {WSI_object.slide_name}, skipping.")
            already_processed = True
            WSI_object.load_patches(os.path.join(directory_patches, f"{WSI_object.slide_name}.{PATCH_EXTS_MAP[patch_exts[0]]}"))
            # Check if the patches are empty
            if WSI_object.coords is None:
                raise RuntimeError(f"Found a patches file for {WSI_object.slide_name}, but loading did not changed WSI_object.coords. " \
                                   "Please check the file.")
            else:
                return already_processed, len(WSI_object.coords)
    if params_patches["mode"] == "roi":
        # Set the region of interest for the image
        if roi_csv is None:
            raise ValueError("If the mode is 'roi', you must provide a valid path to a csv file with the ROI coordinates for each slide.")
        if not os.path.exists(roi_csv):
            raise FileNotFoundError(f"ROI CSV file not found.")
        else:
            WSI_object.set_roi(rois_df_path=roi_csv)
    
    elif params_patches["mode"] == "contours":
        # Load the contours for the image
        if contours_directory is None:
            raise ValueError("If the mode is 'contours', you must provide a directory with contours annotations. " \
        "Please use the `contour` command to extract contours first.")
        contours_path = os.path.join(contours_directory, f"{WSI_object.slide_name}.pkl")
        if not force_patch_extraction:
            if not os.path.exists(contours_path):
                raise FileNotFoundError(f"Contours for the slide {WSI_object.slide_name} not found in {contours_directory}." \
                                        "Please use the `contour` command to extract contours saved as pickle files.")
            else:
                WSI_object.load_tissue_contours(contours_path)
        else:
            if not os.path.exists(contours_path):
                log.warning(f"Contours for the slide {WSI_object.slide_name} not found in {contours_directory}. " \
                            "Using default extraction mode 'all'.")
                params_patches["mode"] = "all"
            else:
                WSI_object.load_tissue_contours(contours_path)
                if WSI_object.tissue_contours is None or len(WSI_object.tissue_contours) == 0:
                    log.warning(f"Contours for the slide {WSI_object.slide_name} are empty. " \
                                "Using default contours extraction mode 'all'.")
                    params_patches["mode"] = "all"

    # Extract patches from the contours
    WSI_object.extract_patches(**params_patches, num_workers=num_workers)
    # Check if the patches are empty
    if WSI_object.coords is None:
        raise RuntimeError(f"extract_patches for {WSI_object.slide_name} did not change WSI_object.coords.")
    # Save the extracted patches
    for patch_ext in patch_exts:
        WSI_object.save_patches(directory_patches, file_format=patch_ext)
    if stitch:
        # Stitch the extracted patches
        if params_stitch_WSI is None or directory_stitch is None:
            raise ValueError("Parameters for stitching or directory for saving stitched images are not provided.")
        if params_stitch_WSI["vis_level"] >= len(WSI_object.level_dimensions):
            log.warning(
                f"Visualization level {params_stitch_WSI['vis_level']} is greater than the number of levels in the WSI. "
                "Using the highest available level for stitching."
            )
            params_stitch_WSI["vis_level"] = len(WSI_object.level_dimensions) - 1
        img = WSI_object.stitch(**params_stitch_WSI)

        img.save(os.path.join(directory_stitch, f"{WSI_object.slide_name}.jpg"))
    return already_processed, len(WSI_object.coords)