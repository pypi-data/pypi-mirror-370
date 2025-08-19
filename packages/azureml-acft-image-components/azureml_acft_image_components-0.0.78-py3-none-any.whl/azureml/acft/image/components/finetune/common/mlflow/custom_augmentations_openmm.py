# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Custom openmmlab augmentations."""
import torch
import numpy as np
from mmdet.datasets.pipelines import Compose
from mmtrack.datasets.pipelines import PIPELINES

__all__ = [
    'PIPELINES', 'LoadTrack', 'VideoCollectForModel'
]


@PIPELINES.register_module(force=True)
class LoadTrack(object):
    """load track annotations.
    """

    def __call__(self, results):
        """Call function.

        For each dict in results, call the call function of `LoadAnnotations`
        to load annotation.

        Args:
            results (dict): Result dict from :obj:`mmtrack.CocoVideoDataset`.
        """
        results['gt_instance_ids'] = results['ann_info']['instance_ids'].copy()
        return results

    def __repr__(self):
        """ print func """
        return self.__class__.__name__


@PIPELINES.register_module(force=True)
class VideoCollectForModel(object):
    """Collect data from the loader relevant to the specific task.

    Args:
        keys (Sequence[str]): Keys of results to be collected in ``data``.
        meta_keys (Sequence[str]): Meta keys to be converted to
            ``mmcv.DataContainer`` and collected in ``data[img_metas]``.
            Defaults to None.
        default_meta_keys (tuple): Default meta keys. Defaults to ('filename',
            'ori_filename', 'ori_shape', 'img_shape', 'pad_shape',
            'scale_factor', 'flip', 'flip_direction', 'img_norm_cfg',
            'frame_id', 'is_video_data').
    """

    def __init__(self,
                 keys=('img', 'gt_bboxes', 'gt_labels', 'gt_instance_ids', 'gt_bboxes_ignore'),
                 meta_keys=None,
                 default_meta_keys=('filename', 'ori_filename', 'ori_shape',
                                    'img_shape', 'pad_shape', 'scale_factor',
                                    'flip', 'flip_direction', 'img_norm_cfg',
                                    'frame_id', 'video_name', 'is_video_data')):
        """ initialization that sets keys and meta_keys
        """
        self.keys = keys
        self.meta_keys = default_meta_keys
        if meta_keys is not None:
            if isinstance(meta_keys, str):
                meta_keys = (meta_keys, )
            else:
                assert isinstance(meta_keys, tuple), \
                    'meta_keys must be str or tuple'
            self.meta_keys += meta_keys

    def __call__(self, results):
        """Call function to collect keys in results.

        The keys in ``meta_keys`` and ``default_meta_keys`` will be converted
        to :obj:mmcv.DataContainer.

        Args:
            results (dict): List of dict or dict which contains
                the data to collect.

        Returns:
            dict: List of dict or dict that contains the
            following keys:

            - keys in ``self.keys``
            - ``img_metas``
        """
        results = self._add_default_meta_keys(results)
        results = self._collect_meta_keys(results)
        return results

    def _collect_meta_keys(self, results):
        """Collect `self.keys` and `self.meta_keys` from `results` (dict)."""
        data = {}
        img_meta = {}
        for key in self.meta_keys:
            if key in results:
                img_meta[key] = results[key]
            elif key in results['img_info']:
                img_meta[key] = results['img_info'][key]
        data['img_metas'] = img_meta
        # data['img'] = results['img']
        for key in self.keys:
            if key == "img":
                data[key] = results[key]
            else:
                data[key] = torch.tensor(results[key])
        return data

    def _add_default_meta_keys(self, results):
        """Add default meta keys.

        We set default meta keys including `pad_shape`, `scale_factor` and
        `img_norm_cfg` to avoid the case where no `Resize`, `Normalize` and
        `Pad` are implemented during the whole pipeline.

        Args:
            results (dict): Result dict contains the data to convert.

        Returns:
            results (dict): Updated result dict contains the data to convert.
        """
        img = results['img']
        results.setdefault('pad_shape', img.shape)
        results.setdefault('scale_factor', 1.0)
        num_channels = 1 if len(img.shape) < 3 else img.shape[2]
        results.setdefault(
            'img_norm_cfg',
            dict(
                mean=np.zeros(num_channels, dtype=np.float32),
                std=np.ones(num_channels, dtype=np.float32),
                to_rgb=False))
        return results

    def __repr__(self):
        """ print func """
        return self.__class__.__name__ + \
            f'(keys={self.keys}, meta_keys={self.meta_keys})'


def compose(pipeline_list: list):
    """ compose list of pipelines"""
    return Compose(pipeline_list)
