import os
import argparse
import yaml
import sys
import segmentedcreator.tooldata as td # type: ignore
import subprocess

def parse_arguments(config_path="config.yaml"):
    parser = argparse.ArgumentParser(description="Video processing")
    parser.add_argument("--root", type=str, default=None, help="Path to the video file")
    parser.add_argument("--fac", type=int, help="Scaling factor for resizing images")
    parser.add_argument("--model_cfg", type=str, default="configs/sam2.1/sam2.1_hiera_l.yaml", help="Path to the SAM2 model configuration file")
    parser.add_argument("--sam2_chkpt", type=str, default=None, help="Path to the SAM2 model checkpoint file")
    parser.add_argument("--n_imgs", type=int, default=100, help="Number of images to process per batch")
    parser.add_argument("--n_obj", type=int, default=20, help="Number of objects to process per batch")
    parser.add_argument("--img_size_sahi", type=int, default=512, help="Image size for the SAHI model")
    parser.add_argument("--overlap_sahi", type=float, default=0.2, help="Overlap threshold for SAHI detections")

    args = parser.parse_args()

    # Load previous config if it exists
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        # Fill in any unspecified CLI arguments
        for key, value in config_data.items():
            if getattr(args, key) is None:
                setattr(args, key, value)

    return args

def check_args(args):
    if args.fac is None:
        raise ValueError("The scale factor (--fac) is mandatory. At least on the first run.")
    if args.sam2_chkpt is None:
        raise ValueError("The path to the SAM2 model checkpoint (--sam2_chkpt) is mandatory. At least on the first run.")

def guardar_configuracion(args, config_path="config.yaml"):
    # Load current configuration if it exists
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
    else:
        config_data = {}

    # Update with current values
    config_data.update({k: v for k, v in vars(args).items() if v is not None})

    with open(config_path, "w") as f:
        yaml.dump(config_data, f)

def process_step():
    print("Starting processing steps...")

    print("####################\n" \
    "Running first step...\n"
    "####################")
    subprocess.run(["uv", "run", "python", "-m", "segmentedcreator.first_step"])

    print("####################\n" \
    "Running second step...\n"
    "####################")
    subprocess.run(["uv", "run", "python", "-m", "segmentedcreator.second_step"])

    print("####################\n" \
    "Running third step...\n"
    "####################")
    subprocess.run(["uv", "run", "python", "-m", "segmentedcreator.third_step"])

    print("####################\n" \
    "Running fourth step...\n"
    "####################")
    subprocess.run(["uv", "run", "python", "-m", "segmentedcreator.fourth_step"])

    print("####################\n" \
    "Running fifth step...\n"
    "####################")
    subprocess.run(["uv", "run", "python", "-m", "segmentedcreator.fifth_step"])

    print("####################\n" \
    "Running sixth step...\n"
    "####################")
    subprocess.run(["uv", "run", "python", "-m", "segmentedcreator.sixth_step"])


def main():
    # Parse the command line arguments
    args = parse_arguments()
    # Check the necessary arguments
    check_args(args)
    # Create the necessary folders
    folders = td.folder_creation(args.root)
    # Save the configuration to a YAML file
    guardar_configuracion(args)

    try:
        process_step()
        #td.group_masks_color(folders["mask_folder"], folders["semantic_folder"])
    except Exception as e:
        sys.exit(f"Error processing video: {e}")

if __name__ == "__main__":
    main()