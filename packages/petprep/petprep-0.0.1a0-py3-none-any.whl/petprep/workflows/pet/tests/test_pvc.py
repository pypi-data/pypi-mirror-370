from pathlib import Path

import pytest
from niworkflows.utils.testing import generate_bids_skeleton

from ....data import load
from ...tests import mock_config
from ..pvc import init_pet_pvc_wf
from .test_base import BASE_LAYOUT, _prep_pet_series


def test_pvc_agtm_nodes(bids_root: Path):
    _prep_pet_series(bids_root)
    config_path = load('pvc/config.json').absolute()
    with mock_config(bids_dir=bids_root):
        wf = init_pet_pvc_wf(tool='petsurfer', method='AGTM', config_path=config_path)
    names = [n.name for n in wf._get_all_nodes()]
    assert 'mean_pet' in names
    assert 'petsurfer_agtm_estimate_psf' in names
    assert 'petsurfer_agtm_pvc_node' in names


@pytest.fixture(scope='module')
def bids_root(tmp_path_factory):
    base = tmp_path_factory.mktemp('pvc')
    bids_dir = base / 'bids'
    generate_bids_skeleton(bids_dir, BASE_LAYOUT)
    return bids_dir
