from pathlib import Path

import nibabel as nb
import numpy as np
from nipype.pipeline import engine as pe

from petprep.interfaces.maths import CropAroundMask, Label2Mask


def _make_nifti(data, fname):
    nb.Nifti1Image(np.asarray(data), np.eye(4)).to_filename(fname)


def test_Label2Mask(tmp_path):
    seg = tmp_path / 'seg.nii.gz'
    data = np.zeros((3, 3, 3), dtype=np.uint16)
    data[1, 2, 0] = 5
    _make_nifti(data, seg)

    node = pe.Node(Label2Mask(in_file=str(seg), label_val=5), name='l2m', base_dir=str(tmp_path))
    result = node.run()

    expected = tmp_path / 'l2m' / 'seg_mask.nii.gz'
    assert Path(result.outputs.out_file) == expected
    out_data = nb.load(result.outputs.out_file).get_fdata()
    assert out_data.dtype == np.float64  # nibabel loads as float64 by default
    assert out_data.sum() == 1
    assert out_data[1, 2, 0] == 1


def test_CropAroundMask(tmp_path):
    in_file = tmp_path / 'input.nii.gz'
    mask_file = tmp_path / 'mask.nii.gz'

    data = np.arange(125).reshape((5, 5, 5)).astype(np.float32)
    _make_nifti(data, in_file)

    mask = np.zeros((5, 5, 5), dtype=np.uint8)
    mask[1:4, 2:5, 0:3] = 1
    _make_nifti(mask, mask_file)

    node = pe.Node(
        CropAroundMask(in_file=str(in_file), mask_file=str(mask_file)),
        name='crop',
        base_dir=str(tmp_path),
    )
    result = node.run()
    expected = tmp_path / 'crop' / 'input_crop.nii.gz'
    assert Path(result.outputs.out_file) == expected

    out_img = nb.load(result.outputs.out_file)
    assert out_img.shape == (3, 3, 3)
    assert np.allclose(out_img.get_fdata(), data[1:4, 2:5, 0:3])
    assert np.allclose(out_img.affine[:3, 3], [1, 2, 0])


def test_CropAroundMask_empty(tmp_path):
    in_file = tmp_path / 'input.nii.gz'
    mask_file = tmp_path / 'mask.nii.gz'

    data = np.zeros((5, 5, 5), dtype=np.float32)
    _make_nifti(data, in_file)
    _make_nifti(np.zeros((5, 5, 5), dtype=np.uint8), mask_file)

    node = pe.Node(
        CropAroundMask(in_file=str(in_file), mask_file=str(mask_file)),
        name='crop',
        base_dir=str(tmp_path),
    )
    result = node.run()

    assert Path(result.outputs.out_file) == in_file
