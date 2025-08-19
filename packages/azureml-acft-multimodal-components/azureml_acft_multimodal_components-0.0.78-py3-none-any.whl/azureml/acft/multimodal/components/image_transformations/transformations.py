# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from torchvision import transforms
from azureml.acft.multimodal.components.constants.constants import ModelTypes, DatasetSplit


def get_transform_function(model_type):
    if model_type == ModelTypes.CLIP:
        return get_image_transforms_fn_for_clip
    else:
        return get_image_transforms_fn_for_mmeft


def get_image_transforms_fn_for_mmeft(self, data_split):
    """Get the transforms to be applied based on data_mode"""

    def transform(examples):
        if data_split == DatasetSplit.TRAIN:
            image_transforms = transforms.Compose([
                transforms.RandomResizedCrop(self.input_size),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
        elif data_split == DatasetSplit.VALIDATION:
            image_transforms = transforms.Compose([
                transforms.Resize(self.input_size),
                transforms.CenterCrop(self.input_size),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
        elif data_split == DatasetSplit.TEST:
            image_transforms = transforms.Compose([
                transforms.Resize(self.input_size),
                transforms.CenterCrop(self.input_size),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])

        if self.image_column_name in examples:
            examples[self.image_column_name] = [image_transforms(image.convert("RGB")) if image is not None else None
                                                for image in examples[self.image_column_name]]
        return examples

    return transform


def get_image_transforms_fn_for_clip(self, data_split):
    """Get the transforms to be applied based on data_mode"""
    return None
