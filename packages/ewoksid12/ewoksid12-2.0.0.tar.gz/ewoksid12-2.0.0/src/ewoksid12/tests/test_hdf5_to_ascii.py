from __future__ import annotations

import os

import h5py
import pytest

from ..tasks.hdf5_to_ascii import Hdf5ToAscii


@pytest.mark.parametrize(
    "counters",
    [
        ["counter1", "counter2"],
        "all",
        ["counter2", "all"],
        ["counter2"],
    ],
)
def test_hdf5_to_spec_counters(tmp_path, counters: list[str] | str) -> None:
    filename = tmp_path / "RAW_DATA" / "bliss_dataset.h5"
    filename.parent.mkdir()
    filename = str(filename)
    output_dir = str(tmp_path / "PROCESSED_DATA")

    nscans = 3
    nchannels = 10
    with h5py.File(filename, "w") as nxroot:
        for scan in range(1, nscans + 1):
            _save_scan_content(nxroot, scan, nchannels)

    inputs = {
        "filename": filename,
        "scan_numbers": list(range(1, nscans + 1)),
        "output_dir": output_dir,
        "counters": counters,
    }
    task = Hdf5ToAscii(inputs=inputs)
    task.run()

    output_filenames = [
        f"scan{i:03d}_1_bliss_dataset.dat" for i in range(1, nscans + 1)
    ]
    output_values = task.get_output_values()
    assert output_values["output_filenames"] == output_filenames

    counters = output_values["counters"]
    _assert_ascii_content(output_dir, output_filenames, counters, nchannels)


def test_hdf5_to_spec_with_subscan(tmp_path) -> None:
    filename = tmp_path / "RAW_DATA" / "bliss_dataset.h5"
    filename.parent.mkdir()
    filename = str(filename)
    output_dir = str(tmp_path / "PROCESSED_DATA")

    nscans = 2
    nchannels = 10
    with h5py.File(filename, "w") as nxroot:
        for scan in range(1, nscans + 1):
            _save_scan_content(nxroot, scan, nchannels)

    inputs = {
        "filename": filename,
        "scan_numbers": list(range(1, nscans + 1)),
        "output_dir": output_dir,
        "counters": "all",
        "has_subscan": True,
    }
    task = Hdf5ToAscii(inputs=inputs)
    task.run()

    output_filenames = [
        f"scan{j:03d}_{i}_bliss_dataset.dat"
        for i in [1, 2]
        for j in range(1, nscans + 1)
    ]
    output_values = task.get_output_values()
    assert output_values["output_filenames"] == output_filenames

    counters = output_values["counters"]
    _assert_ascii_content(output_dir, output_filenames, counters, nchannels)


def test_hdf5_to_spec_failed(tmp_path) -> None:
    filename = tmp_path / "RAW_DATA" / "bliss_dataset.h5"
    filename.parent.mkdir()
    filename = str(filename)
    output_dir = str(tmp_path / "PROCESSED_DATA")

    nscans = 1
    nchannels = 10
    with h5py.File(filename, "w") as nxroot:
        for scan in range(1, nscans + 1):
            _save_scan_content(nxroot, scan, nchannels)

    inputs = {
        "filename": filename,
        "scan_numbers": list(range(1, nscans + 3)),
        "output_dir": output_dir,
        "counters": ["counter1", "counter2"],
        "retry_timeout": 0.1,
    }
    task = Hdf5ToAscii(inputs=inputs)
    with pytest.raises(
        RuntimeError, match=r"^Failed scans \(see logs why\): \['2', '3'\]$"
    ):
        task.run()

    output_filenames = ["scan001_1_bliss_dataset.dat"]
    counters = [inputs["counters"]]
    _assert_ascii_content(output_dir, output_filenames, counters, nchannels)


def _save_scan_content(nxroot: h5py.Group, scan: int, nchannels: int) -> None:
    counters = ["counter1", "counter2"]
    for subscan in [1, 2]:
        nxroot[f"/{scan}.{subscan}/start_time"] = "start_time"
        nxroot[f"/{scan}.{subscan}/title"] = f"timescan 0.1 {subscan}"
        if subscan == 2:
            counters.append("counter3")
        for counter in counters:
            factor = 10 ** (int(counter[-1]) - 1)
            dataset = [scan + i / factor for i in range(nchannels)]
            nxroot[f"/{scan}.{subscan}/measurement/{counter}"] = dataset
        nxroot[f"/{scan}.{subscan}/end_time"] = "end_time"


def _assert_ascii_content(
    output_dir: str,
    output_filenames: list[str],
    counters: list[list[str]],
    nchannels: int,
) -> None:
    for output_filename, scan_counters in zip(output_filenames, counters):
        scan = int(output_filename.split("_")[0][4:])
        with open(os.path.join(output_dir, output_filename), "r") as f:
            header = "  ".join(scan_counters)
            expected_lines = [header]
            for i in range(nchannels):
                values = []
                for scan_counter in scan_counters:
                    # Calculate factor based on the suffix of the scan counter name.
                    factor = 10 ** (int(scan_counter[-1]) - 1)
                    value = scan + i / factor
                    values.append(str(value))
                expected_lines.extend([" ".join(values)])

            actual_lines = [s.rstrip() for s in f.readlines()]
            assert actual_lines == expected_lines
