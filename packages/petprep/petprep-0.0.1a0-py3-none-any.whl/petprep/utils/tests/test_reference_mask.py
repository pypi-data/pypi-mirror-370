import nibabel as nb
import numpy as np

from petprep.utils.reference_mask import generate_reference_region


def test_generate_reference_region_target_volume():
    seg = np.zeros((10, 10, 10), dtype=np.int16)
    seg[3:7, 3:7, 3:7] = 1
    img = nb.Nifti1Image(seg, np.eye(4))

    config = {
        'refmask_indices': [1],
        'smooth_fwhm_mm': 2.3548,
        'target_volume_ml': 0.04,
    }

    out_img = generate_reference_region(img, config)
    mask = out_img.get_fdata()
    voxel_vol_ml = np.prod(out_img.header.get_zooms()) / 1000.0
    volume_ml = mask.sum() * voxel_vol_ml
    assert np.isclose(volume_ml, config['target_volume_ml'], atol=0.001)


def test_generate_reference_region_exclude(tmp_path):
    data = np.zeros((5, 5, 5), dtype=np.uint8)
    data[2, 2, 2] = 1
    data[2, 2, 3] = 2
    seg = nb.Nifti1Image(data, np.eye(4))
    config = {'refmask_indices': [1, 2], 'exclude_indices': [2]}
    out = generate_reference_region(seg, config).get_fdata()
    assert out[2, 2, 3] == 0
    assert out[2, 2, 2] == 1
    assert out.sum() == 1


def test_generate_reference_region_exclude_dilate(tmp_path):
    data = np.zeros((5, 5, 5), dtype=np.uint8)
    data[2, 2, 2] = 1
    data[2, 2, 3] = 2
    seg = nb.Nifti1Image(data, np.eye(4))
    config = {
        'refmask_indices': [1, 2],
        'exclude_indices': [2],
        'dilate_by_voxels': 1,
    }
    out = generate_reference_region(seg, config).get_fdata()
    assert out.sum() == 0


def test_generate_reference_region_large_target_volume():
    seg = np.zeros((5, 5, 5), dtype=np.int16)
    seg[1:4, 1:4, 1:4] = 1
    img = nb.Nifti1Image(seg, np.eye(4))

    config = {
        'refmask_indices': [1],
        'smooth_fwhm_mm': 2.3548,
        'target_volume_ml': 10.0,
    }

    out_img = generate_reference_region(img, config)
    mask = out_img.get_fdata()
    assert mask.sum() == seg.sum()


def test_generate_reference_region_gm_threshold():
    seg = np.zeros((5, 5, 5), dtype=np.uint8)
    seg[2, 2, 2] = 1
    seg[3, 3, 3] = 1
    seg_img = nb.Nifti1Image(seg, np.eye(4))

    gm = np.zeros((5, 5, 5), dtype=np.float32)
    gm[2, 2, 2] = 0.4
    gm[3, 3, 3] = 0.8
    gm_img = nb.Nifti1Image(gm, np.eye(4))

    config = {'refmask_indices': [1], 'gm_prob_threshold': 0.5}

    out = generate_reference_region(seg_img, config, gm_probseg_img=gm_img)
    data = out.get_fdata()
    assert data.sum() == 1
    assert data[3, 3, 3] == 1
