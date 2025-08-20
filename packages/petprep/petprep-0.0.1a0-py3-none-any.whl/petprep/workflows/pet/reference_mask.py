# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
#
# Copyright The NiPreps Developers <nipreps@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# We support and encourage derived works from this project, please read
# about our expectations at
#
#     https://www.nipreps.org/community/licensing/
#
"""Workflows for creation of reference masks."""

from __future__ import annotations

import nipype.pipeline.engine as pe

from petprep.interfaces.reference_mask import ExtractRefRegion


def init_pet_refmask_wf(
    *,
    segmentation: str,
    ref_mask_name: str,
    ref_mask_index: list[int] | None = None,
    config_path: str,
    name: str = 'pet_refmask_wf',
) -> pe.Workflow:
    import nipype.pipeline.engine as pe
    from nipype.interfaces.utility import IdentityInterface

    workflow = pe.Workflow(name=name)

    inputnode = pe.Node(
        IdentityInterface(fields=['seg_file', 'gm_probseg']),
        name='inputnode',
    )
    outputnode = pe.Node(IdentityInterface(fields=['refmask_file']), name='outputnode')

    extract_mask = pe.Node(ExtractRefRegion(), name='extract_refregion')
    extract_mask.inputs.segmentation_type = segmentation
    extract_mask.inputs.region_name = ref_mask_name
    extract_mask.inputs.config_file = config_path

    if ref_mask_index is not None:
        # Override config-based lookup and force manual indices
        extract_mask.inputs.override_indices = ref_mask_index

    workflow.connect(
        [
            (
                inputnode,
                extract_mask,
                [
                    ('seg_file', 'seg_file'),
                    ('gm_probseg', 'gm_probseg'),
                ],
            ),
            (extract_mask, outputnode, [('refmask_file', 'refmask_file')]),
        ]
    )

    return workflow
