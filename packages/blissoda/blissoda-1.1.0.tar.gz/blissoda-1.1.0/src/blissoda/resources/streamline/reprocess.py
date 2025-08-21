import os
import json
import logging
from glob import glob
from silx.io.h5py_utils import open_item
from silx.io.url import DataUrl
from ewoks import execute_graph
from ewoksjob.client import submit


def extract_distance(image_url: str):
    image_url = "/".join(image_url.split("/")[:-2])
    dataurl = DataUrl(image_url)
    with open_item(dataurl.file_path(), dataurl.data_path()) as scan:
        positioners = scan["instrument/positioners"]
        return positioners["cncx"][()]


def modify_workflow(old_processed: str, new_processed: str, workflow: dict):
    # Modify destination for results
    for nodeattrs in workflow["nodes"]:
        for idict in nodeattrs.get("default_inputs", list()):
            if (
                isinstance(idict["value"], str)
                and old_processed in idict["value"]
                and "ring_detection" not in idict["value"]
            ):
                idict["value"] = idict["value"].replace(old_processed, new_processed)

    # Modify integration parameter
    newmake = "fabio:///data/visitor/in1029/id31/20230523/PROCESSED_DATA/calibration/PDF_mask_without_corner.edf"
    is_pdf = False
    for nodeattrs in workflow["nodes"]:
        if "Integrate1D" in nodeattrs["task_identifier"]:
            for param in nodeattrs["default_inputs"]:
                if param["name"] == "image":
                    is_pdf = int(extract_distance(param["value"])) == 300

    for nodeattrs in workflow["nodes"]:
        if "PyFaiConfig" in nodeattrs["task_identifier"]:
            for param in nodeattrs["default_inputs"]:
                if param["name"] == "filename":
                    if is_pdf:
                        param["value"] = (
                            "/data/visitor/in1029/id31/20230523/PROCESSED_DATA/calibration/PDF_jason_MM.json"
                        )
                    else:
                        param["value"] = (
                            "/data/visitor/in1029/id31/20230523/PROCESSED_DATA/calibration/WAXS_jason_MM.json"
                        )
                if param["name"] == "integration_options":
                    if is_pdf:
                        param["value"]["nbpt_rad"] = 3000
                    else:
                        param["value"]["nbpt_rad"] = 9000
                    param["value"]["mask_file"] = newmake


def reprocess(
    proposal: str,
    session: str,
    process_name: str,
    beamline: str = "id31",
    persist: bool = False,
) -> None:
    remote = os.environ.get("BEACON_HOST")
    if not remote:
        logging.basicConfig(level=logging.INFO)
    processed_dir = f"/data/visitor/{proposal}/{beamline}/{session}/PROCESSED_DATA/"
    backup_dir = f"/data/visitor/{proposal}/{beamline}/{session}/NOBACKUP/"

    workflows = glob(os.path.join(processed_dir, "streamline", "*", "*.json"))
    for wffilename in workflows:
        with open(wffilename, "r") as f:
            workflow = json.load(f)

        kwargs = dict()
        if persist:
            kwargs["varinfo"] = {"root_uri": backup_dir, "scheme": "nexus"}

        old_processed = os.path.join("PROCESSED_DATA", "streamline")
        new_processed = os.path.join("PROCESSED_DATA", process_name)
        kwargs["convert_destination"] = wffilename.replace(old_processed, new_processed)

        modify_workflow(old_processed, new_processed, workflow)

        if remote:
            submit(args=(workflow,), kwargs=kwargs)
        else:
            execute_graph(workflow, **kwargs)


if __name__ == "__main__":
    # os.environ["BEACON_HOST"] = "id31:25000"
    reprocess("in1029", "20230523", "streamline_fixmask")
