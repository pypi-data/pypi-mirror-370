from __future__ import annotations

import logging
import os
from typing import Any

from blissdata.h5api import dynamic_hdf5
from ewokscore.task import Task

from .io import save_as_ascii

logger = logging.getLogger(__name__)


class Hdf5ToAscii(
    Task,
    input_names=["filename", "output_dir"],
    optional_input_names=[
        "scan_numbers",
        "retry_timeout",
        "retry_period",
        "counters",
        "has_subscan",
    ],
    output_names=["counters", "output_filenames"],
):
    """Save 1D data from Bliss HDF5 scans in ID12 ASCII files."""

    def run(self) -> None:
        filename: str = self.inputs.filename
        scan_numbers: list[int] | None = self.get_input_value("scan_numbers", None)
        retry_timeout: float | None = self.get_input_value("retry_timeout", None)
        retry_period: float | None = self.get_input_value("retry_period", 1)
        raw_counters: list[str] | str = self.get_input_value("counters", "all")
        has_subscan: bool = self.get_input_value("has_subscan", False)

        # Convert counters to a list if it is a string.
        if isinstance(raw_counters, str):
            raw_counters = [raw_counters]

        output_dir: str = self.inputs.output_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        output_filenames: list[str] = []
        scans_counters: list[list[str]] = []
        failed_scans: list[str] = []

        with dynamic_hdf5.File(
            filename, retry_timeout=retry_timeout, retry_period=retry_period
        ) as nxroot:
            scan_names: list[str]
            if scan_numbers:
                scan_names = [f"{scannr}.1" for scannr in scan_numbers]
                if has_subscan:
                    scan_names.extend([f"{scannr}.2" for scannr in scan_numbers])
            else:
                # Convert HDF5 file top-level groups to a list of strings.
                scan_names = list(nxroot)

            for scan_name in scan_names:
                scan_number, subscan_number = scan_name.split(".")
                try:
                    _ = nxroot[f"/{scan_name}/end_time"]  # wait for scan to finish
                    measurement = nxroot[f"/{scan_name}/measurement"]
                    data: dict[str, Any] = {}

                    # Create a fresh list of counters for each scan.
                    scan_counters: list[str] = list(raw_counters)

                    # Replace all occurrence of "all".
                    if "all" in scan_counters:
                        while "all" in scan_counters:
                            scan_counters.remove("all")
                        scan_counters.extend(measurement.keys())

                    # Remove duplicates while preserving order.
                    scan_counters = list(dict.fromkeys(scan_counters))

                    for scan_counter in scan_counters:
                        try:
                            dataset = measurement[scan_counter]
                        except Exception as e:
                            logger.warning(
                                "Skipping counter '%s' in scan %s: %s (%s)",
                                scan_counter,
                                scan_name,
                                str(e),
                                e.__class__.__name__,
                            )
                            continue
                        if dataset.ndim == 1:
                            data[scan_counter] = dataset[()]
                except Exception as e:
                    failed_scans.append(scan_number)
                    logger.error(
                        "Processing scan %s::/%s failed (%s)", filename, scan_name, e
                    )
                    continue

                if not data:
                    # Scan has no data to save
                    continue

                stem = os.path.splitext(os.path.basename(filename))[0]
                output_filename = (
                    f"scan{int(scan_number):03d}_{subscan_number}_{stem}.dat"
                )

                save_as_ascii(os.path.join(output_dir, output_filename), data)
                output_filenames.append(output_filename)
                scans_counters.append(scan_counters)

        if failed_scans:
            raise RuntimeError(f"Failed scans (see logs why): {failed_scans}")

        self.outputs.counters = scans_counters
        self.outputs.output_filenames = output_filenames
