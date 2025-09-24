import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from shapely.geometry import Point

# FastAI imports
from fastai.vision.all import *
from fastai.data.transforms import RandomSplitter
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import pickle
import torch
import torch.nn as nn

# TIMM imports for Vision Transformers
import timm
from timm import create_model

os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# Utility Functions and Unified Config
class UnifiedConfig:
    """Unified configuration for BIA4 pipeline with optional advanced settings"""
    SEED = 42
    IMG_SIZE = 224
    BATCH_SIZE = 32
    VALID_PCT = 0.2
    BIA4_INSIDE_CATEGORY_ID = 3
    EPOCHS_STAGE1 = 5
    EPOCHS_STAGE2 = 10

    def __init__(self, base_dir: str = None, advanced: bool = False):
        self.BASE_DIR = Path(base_dir or Path(__file__).parent.parent.resolve() / 'datasets' / 'bia4')
        self.COCO_JSON_PATH = str(self.BASE_DIR / 'All-Coco-3.json')
        self.AUGMENTED_DIR = str(self.BASE_DIR / 'augmented')
        self.AUGMENTED_JSON_PATH = str(self.BASE_DIR / 'augmented' / 'augmented_coco.json')
        self.MERGED_JSON_PATH = str(self.BASE_DIR / 'All-Coco-3-merged.json')
        self.MODEL_SAVE_PATH = str(self.BASE_DIR / 'models' / 'bia4_inside_model.pkl')

        if advanced:
            self.ENSEMBLE_MODELS_DIR = str(self.BASE_DIR / 'ensemble_models')
            self.ENSEMBLE_PREDICTIONS_PATH = str(self.BASE_DIR / 'ensemble_predictions.pkl')
            self.ARCHITECTURES = {
                'resnet50': resnet50,
                'resnet101': resnet101,
                'efficientnet_b0': 'efficientnet_b0',
                'efficientnet_b3': 'efficientnet_b3',
                'vit_base_patch16_224': 'vit_base_patch16_224',
                'vit_small_patch16_224': 'vit_small_patch16_224',
                'swin_base_patch4_window7_224': 'swin_base_patch4_window7_224',
                'convnext_base': 'convnext_base'
            }

def set_random_seeds(seed: int) -> None:
    """Set random seeds for reproducibility"""
    set_seed(seed, reproducible=True)
    torch.manual_seed(seed)
    np.random.seed(seed)

def load_coco_data(json_path: str, base_image_dir: str = None) -> Tuple[Dict[str, Any], Path]:
    """Load COCO JSON data with flexible image path"""
    base_image_dir = Path(base_image_dir).resolve() if base_image_dir else Path(json_path).parent.resolve()
    with open(json_path, 'r') as f:
        return json.load(f), base_image_dir

def save_coco_data(data: Dict[str, Any], output_path: str) -> None:
    """Save COCO JSON data"""
    os.makedirs(Path(output_path).parent, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

def create_label_dataframe(coco_data: Dict[str, Any], base_image_dir: Path, config: UnifiedConfig) -> pd.DataFrame:
    """Create DataFrame with image paths and labels"""
    data = []
    annotations_by_image, bia4_annotations_by_image = _build_annotations_index(coco_data['annotations'], config)

    for img in coco_data['images']:
        img_id = img['id']
        img_path = base_image_dir / img['file_name']
        img_center = (img['width'] / 2, img['height'] / 2)
        label = _is_bia4_inside_center(img_id, img_center, bia4_annotations_by_image, config)
        data.append([str(img_path), label])

    return pd.DataFrame(data, columns=['image_path', 'label'])

def _build_annotations_index(annotations: List[Dict], config: UnifiedConfig) -> Tuple[Dict, Dict]:
    """Build optimized indexes for faster lookup"""
    annotations_by_image = {}
    bia4_annotations_by_image = {}

    for ann in annotations:
        image_id = ann['image_id']
        if image_id not in annotations_by_image:
            annotations_by_image[image_id] = []
        annotations_by_image[image_id].append(ann)

        if ann['category_id'] == config.BIA4_INSIDE_CATEGORY_ID:
            if image_id not in bia4_annotations_by_image:
                bia4_annotations_by_image[image_id] = []
            bia4_annotations_by_image[image_id].append(ann)

    return annotations_by_image, bia4_annotations_by_image

def _is_bia4_inside_center(image_id: int, center_point: Tuple[float, float], 
                          bia4_annotations_by_image: Dict, config: UnifiedConfig) -> bool:
    """Check if center point is inside Bia4_Inside bbox"""
    if image_id not in bia4_annotations_by_image:
        return False
    return any(_point_in_bbox(center_point, ann['bbox']) for ann in bia4_annotations_by_image[image_id])

def _point_in_bbox(point: Tuple[float, float], bbox: List[float]) -> bool:
    """Check if a point is inside a bounding box"""
    x, y = point
    x_min, y_min, width, height = bbox
    return x_min <= x <= x_min + width and y_min <= y <= y_min + height

def load_and_augment_data(config: UnifiedConfig, coco_json_path: str = None, base_image_dir: str = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load and augment dataset, returning combined DataFrame and merged COCO data"""
    processor = CocoDataProcessor(config)
    dataset_builder = Bia4DatasetBuilder(processor)
    augmenter = Bia4Augmenter(processor)

    coco_json_path = coco_json_path or config.COCO_JSON_PATH
    coco_data, base_image_dir = processor.load_coco_data(coco_json_path, base_image_dir)
    df_base = dataset_builder.create_label_dataframe(coco_data)

    aug_json_path = Path(config.AUGMENTED_JSON_PATH)
    if aug_json_path.exists():
        aug_data, _ = processor.load_coco_data(str(aug_json_path), base_image_dir=str(config.AUGMENTED_DIR))
        df_aug = dataset_builder.create_label_dataframe(aug_data)
        aug_json = aug_data
    else:
        df_aug, aug_json = augmenter.augment_dataset(coco_data)
        processor.save_coco_data(aug_json, config.AUGMENTED_JSON_PATH)

    merged_coco = coco_data.copy()
    merged_coco['images'].extend(aug_json['images'])
    merged_coco['annotations'].extend(aug_json['annotations'])
    processor.save_coco_data(merged_coco, config.MERGED_JSON_PATH)

    df_combined = pd.concat([df_base, df_aug], ignore_index=True)
    return df_combined, merged_coco

def predict_and_visualize(config: UnifiedConfig, architectures: List[str], image_path: str) -> Tuple[Dict[str, str], Tuple[float, float]]:
    """Predict on a single image with multiple models and visualize center point"""
    results = {}
    for arch in architectures:
        model_path = Path(config.ENSEMBLE_MODELS_DIR) / f"{arch}_model.pkl"
        if model_path.exists():
            learn = load_learner(model_path)
            pred, pred_idx, probs = learn.predict(image_path)
            results[arch] = 'Bia4_Inside' if pred_idx.item() == 1 else 'Not_Bia4_Inside'

    img = Image.open(image_path)
    center = (img.width / 2, img.height / 2)

    plt.imshow(img)
    plt.scatter(*center, c='r', marker='x')
    plt.show()

    return results, center

# Original Classes with Modifications
class CocoDataProcessor:
    """Processor for COCO format dataset operations"""
    def __init__(self, config: UnifiedConfig):
        self.config = config
    
    def load_coco_data(self, json_path: str, base_image_dir: str = None) -> Tuple[Dict[str, Any], Path]:
        """Load COCO JSON data using utility function"""
        return load_coco_data(json_path, base_image_dir)
    
    def save_coco_data(self, data: Dict[str, Any], output_path: str) -> None:
        """Save COCO JSON data using utility function"""
        save_coco_data(data, output_path)
    
    def point_in_bbox(self, point: Tuple[float, float], bbox: List[float]) -> bool:
        """Check if a point is inside a bounding box"""
        return _point_in_bbox(point, bbox)
    
    def get_image_center(self, image_info: Dict) -> Tuple[float, float]:
        """Get center point of an image"""
        return (image_info['width'] / 2, image_info['height'] / 2)

class Bia4DatasetBuilder:
    """Builder for BIA4 classification dataset"""
    def __init__(self, processor: CocoDataProcessor):
        self.processor = processor
        self.config = processor.config
    
    @property
    def base_image_dir(self) -> Path:
        """Get base image directory from processor or config"""
        if hasattr(self.processor, 'base_image_dir') and self.processor.base_image_dir:
            return Path(self.processor.base_image_dir).resolve()
        return Path(self.config.COCO_JSON_PATH).parent.resolve()
    
    def create_label_dataframe(self, coco_data: Dict[str, Any]) -> pd.DataFrame:
        """Create DataFrame using utility function"""
        return create_label_dataframe(coco_data, self.base_image_dir, self.config)

class Bia4Augmenter:
    """Data augmenter for BIA4 dataset using geometric transformations"""
    def __init__(self, processor: CocoDataProcessor):
        self.processor = processor
        self.config = processor.config
        
    @property
    def base_image_dir(self) -> Path:
        """Get base image directory from processor or config"""
        if hasattr(self.processor, 'base_image_dir') and self.processor.base_image_dir:
            return Path(self.processor.base_image_dir).resolve()
        return Path(self.config.COCO_JSON_PATH).parent.resolve()
    
    @property
    def augmented_dir(self) -> Path:
        """Get augmented directory path"""
        return Path(self.config.AUGMENTED_DIR).resolve()
    
    def create_mask(self, width: int, height: int, segmentation: List[float]) -> np.ndarray:
        """Create binary mask from segmentation points"""
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        
        poly_points = [(segmentation[i], segmentation[i+1]) 
                      for i in range(0, len(segmentation), 2)]
        
        if len(poly_points) < 3:
            return np.zeros((height, width), dtype=np.uint8)
        
        draw.polygon(poly_points, fill=255)
        return np.array(mask)
    
    def augment_dataset(self, coco_data: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Perform center-based augmentation on the dataset"""
        augmented_data = []
        aug_json = {
            "info": coco_data['info'],
            "categories": coco_data['categories'],
            "images": [],
            "annotations": []
        }
        
        self.augmented_dir.mkdir(parents=True, exist_ok=True)
        
        max_img_id = max(img['id'] for img in coco_data['images'])
        max_ann_id = max(ann['id'] for ann in coco_data['annotations'])
        
        for img in coco_data['images']:
            augmentation_result = self._augment_single_image(
                img, coco_data['annotations'], max_img_id, max_ann_id)
            
            if augmentation_result:
                aug_img, aug_ann, new_img_id, new_ann_id = augmentation_result
                full_aug_path = self.augmented_dir / aug_img['file_name']
                augmented_data.append([str(full_aug_path), True])
                aug_json['images'].append(aug_img)
                aug_json['annotations'].append(aug_ann)
                
                max_img_id = new_img_id
                max_ann_id = new_ann_id
        
        return pd.DataFrame(augmented_data, columns=['image_path', 'label']), aug_json
    
    def _augment_single_image(self, 
                            img: Dict, 
                            annotations: List[Dict], 
                            max_img_id: int, 
                            max_ann_id: int) -> Optional[Tuple]:
        """Augment a single image by centering the Bia4_Inside region"""
        img_id = img['id']
        img_path = self.base_image_dir / img['file_name']
        img_center = self.processor.get_image_center(img)
        
        bia4_annotation = self._find_bia4_annotation(img_id, annotations)
        
        if not bia4_annotation or self.processor.point_in_bbox(img_center, bia4_annotation['bbox']):
            return None
        
        augmented_image = self._center_region(img, str(img_path), bia4_annotation, img_center)
        if augmented_image is None:
            return None
        
        new_img_id = max_img_id + 1
        new_ann_id = max_ann_id + 1
        
        aug_img, aug_ann = self._create_augmented_entries(
            img, bia4_annotation, augmented_image, new_img_id, new_ann_id)
        
        return aug_img, aug_ann, new_img_id, new_ann_id
    
    def _find_bia4_annotation(self, image_id: int, annotations: List[Dict]) -> Optional[Dict]:
        """Find Bia4_Inside annotation for given image"""
        for ann in annotations:
            if (ann['image_id'] == image_id and 
                ann['category_id'] == self.config.BIA4_INSIDE_CATEGORY_ID):
                return ann
        return None
    
    def _center_region(self, 
                      img_info: Dict, 
                      img_path: str, 
                      annotation: Dict, 
                      center_point: Tuple[float, float]) -> Optional[Image.Image]:
        """Center the annotated region in the image"""
        try:
            original_img = Image.open(img_path).convert('RGB')
            np_img = np.array(original_img)
            
            mask = self.create_mask(img_info['width'], img_info['height'], 
                                  annotation['segmentation'][0])
            if np.sum(mask) == 0:
                return None
            
            processed_img = self._reposition_region(np_img, mask, annotation, center_point)
            return Image.fromarray(processed_img)
            
        except Exception as e:
            print(f"Error processing image {img_path}: {e}")
            return None
    
    def _reposition_region(self, 
                          image: np.ndarray, 
                          mask: np.ndarray, 
                          annotation: Dict, 
                          center: Tuple[float, float]) -> np.ndarray:
        """Reposition the masked region to center"""
        x_min, y_min, w, h = annotation['bbox']
        seg_h, seg_w = int(h), int(w)
        
        new_x = max(0, min(int(center[0] - seg_w / 2), image.shape[1] - seg_w))
        new_y = max(0, min(int(center[1] - seg_h / 2), image.shape[0] - seg_h))
        
        cut_region = np.zeros_like(image)
        for c in range(3):
            cut_region[:,:,c] = image[:,:,c] * (mask // 255)
        
        result_image = image.copy()
        for c in range(3):
            result_image[:,:,c][mask > 0] = np.mean(result_image[:,:,c])
        
        paste_mask = np.roll(np.roll(mask, new_y - int(y_min), axis=0), 
                           new_x - int(x_min), axis=1)
        
        for c in range(3):
            shifted_cut = np.roll(np.roll(cut_region[:,:,c], 
                                        new_y - int(y_min), axis=0), 
                                new_x - int(x_min), axis=1)
            result_image[:,:,c][paste_mask > 0] = shifted_cut[paste_mask > 0]
        
        return result_image
    
    def _create_augmented_entries(self, 
                                original_img: Dict, 
                                original_ann: Dict, 
                                augmented_image: Image.Image, 
                                new_img_id: int, 
                                new_ann_id: int) -> Tuple[Dict, Dict]:
        """Create COCO entries for augmented image"""
        from uuid import uuid4
        
        aug_filename = f"aug_{original_img['file_name']}"
        aug_path = self.augmented_dir / aug_filename
        augmented_image.save(aug_path)
        
        new_img = {
            "id": new_img_id,
            "datatorch_id": str(uuid4()),
            "storage_id": str(uuid4()),
            "path": aug_filename,
            "width": original_img['width'],
            "height": original_img['height'],
            "file_name": aug_filename,
            "metadata": {},
            "date_captured": original_img['date_captured']
        }
        
        x_min, y_min, w, h = original_ann['bbox']
        img_center = self.processor.get_image_center(original_img)
        new_x = max(0, min(int(img_center[0] - w / 2), original_img['width'] - w))
        new_y = max(0, min(int(img_center[1] - h / 2), original_img['height'] - h))
        
        segmentation = original_ann['segmentation'][0]
        new_seg = [x + (new_x - x_min) for x in segmentation[::2]] + \
                 [y + (new_y - y_min) for y in segmentation[1::2]]
        
        new_ann = {
            "id": new_ann_id,
            "datatorch_id": str(uuid4()),
            "image_id": new_img_id,
            "category_id": self.config.BIA4_INSIDE_CATEGORY_ID,
            "segmentation": [new_seg],
            "area": original_ann['area'],
            "bbox": [new_x, new_y, w, h],
            "iscrowd": 0,
            "metadata": {}
        }
        
        return new_img, new_ann

class DatasetAnalyzer:
    """Analyzer for dataset statistics and visualization"""
    def __init__(self, processor: CocoDataProcessor, display_mode: str = "auto"):
        self.processor = processor
        self.display_mode = self._detect_display_mode(display_mode)
        
    def _detect_display_mode(self, mode: str) -> str:
        """Detect execution environment"""
        if mode != "auto":
            return mode
        try:
            from IPython import get_ipython
            if get_ipython() is not None:
                return "notebook"
        except:
            pass
        import matplotlib
        if matplotlib.get_backend().lower() not in ['agg', 'template']:
            return "notebook"
        return "console"
    
    def analyze_dataset(self, coco_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive dataset statistics"""
        categories = {cat['id']: cat['name'] for cat in coco_data['categories']}
        bia4_count = sum(1 for ann in coco_data['annotations'] 
                        if ann['category_id'] == self.processor.config.BIA4_INSIDE_CATEGORY_ID)
        widths = [img['width'] for img in coco_data['images']]
        heights = [img['height'] for img in coco_data['images']]
        
        category_counts = {}
        for ann in coco_data['annotations']:
            cat_id = ann['category_id']
            category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
        
        report = {
            "summary": {
                "images": len(coco_data['images']),
                "annotations": len(coco_data['annotations']),
                "bia4_inside_annotations": bia4_count,
                "categories": categories
            },
            "size_range": {
                "width": {"min": min(widths), "max": max(widths), "mean": float(np.mean(widths))},
                "height": {"min": min(heights), "max": max(heights), "mean": float(np.mean(heights))}
            },
            "category_distribution": {
                cat['name']: category_counts.get(cat['id'], 0) for cat in coco_data['categories']
            }
        }
        
        print("=== Dataset Analysis ===")
        print(f"Images: {report['summary']['images']}")
        print(f"Annotations: {report['summary']['annotations']}")
        print(f"Bia4_Inside annotations: {report['summary']['bia4_inside_annotations']}")
        print(f"Categories: {report['summary']['categories']}")
        print(f"Image size range: {report['size_range']['width']['min']}-{report['size_range']['width']['max']} x "
              f"{report['size_range']['height']['min']}-{report['size_range']['height']['max']}")
        print("\n=== Category Distribution ===")
        for name, count in report['category_distribution'].items():
            print(f"{name}: {count} annotations")
        
        return report
    
    def plot_label_distribution(self, df: pd.DataFrame, show_plot: bool = True) -> Optional[plt.Figure]:
        """Plot distribution of labels"""
        label_counts = df['label'].value_counts()
        
        if self.display_mode == "console":
            print("\n=== Label Distribution ===")
            print(f"Bia4_Inside (True): {label_counts.get(True, 0)} images")
            print(f"Not Bia4_Inside (False): {label_counts.get(False, 0)} images")
            print(f"Ratio: {label_counts.get(True, 0) / len(label_counts):.2%}")
            
            total = label_counts.sum()
            true_count = label_counts.get(True, 0)
            false_count = label_counts.get(False, 0)
            
            print("\nASCII Chart:")
            true_bars = "█" * int(true_count / total * 50)
            false_bars = "█" * int(false_count / total * 50)
            print(f"True:  {true_bars} ({true_count})")
            print(f"False: {false_bars} ({false_count})")
            return None
        else:
            fig = plt.figure(figsize=(8, 5))
            
            plt.subplot(1, 2, 1)
            label_counts.plot(kind='bar', color=['#1f77b4', '#ff7f0e'])
            plt.title('Bia4_Inside Label Distribution')
            plt.xlabel('Label')
            plt.ylabel('Count')
            plt.xticks([0, 1], ['Not_Bia4_Inside', 'Bia4_Inside'], rotation=45)
            
            plt.subplot(1, 2, 2)
            plt.pie(label_counts.values, labels=label_counts.index, 
                    autopct='%1.1f%%', colors=['#1f77b4', '#ff7f0e'])
            plt.title('Label Proportion')
            
            plt.tight_layout()
            if show_plot:
                plt.show()
            return fig
    
    def plot_image_size_distribution(self, coco_data: Dict[str, Any]) -> Optional[plt.Figure]:
        """Image size distribution"""
        widths = [img['width'] for img in coco_data['images']]
        heights = [img['height'] for img in coco_data['images']]
        
        if self.display_mode == "console":
            print(f"\n=== Image Size Distribution ===")
            print(f"Width: min={min(widths)}, max={max(widths)}, mean={np.mean(widths):.1f}")
            print(f"Height: min={min(heights)}, max={max(heights)}, mean={np.mean(heights):.1f}")
            return None
        else:
            fig = plt.figure(figsize=(10, 4))
            
            plt.subplot(1, 2, 1)
            plt.hist(widths, bins=20, alpha=0.7, color='skyblue')
            plt.title('Image Width Distribution')
            plt.xlabel('Width (pixels)')
            plt.ylabel('Frequency')
            
            plt.subplot(1, 2, 2)
            plt.hist(heights, bins=20, alpha=0.7, color='lightcoral')
            plt.title('Image Height Distribution')
            plt.xlabel('Height (pixels)')
            
            plt.tight_layout()
            plt.show()
            return fig
    
    def generate_report(self, coco_data: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """Generate detailed report dictionary"""
        report = {
            "summary": {
                "total_images": len(coco_data['images']),
                "total_annotations": len(coco_data['annotations']),
                "bia4_inside_annotations": sum(1 for ann in coco_data['annotations'] 
                                             if ann['category_id'] == self.processor.config.BIA4_INSIDE_CATEGORY_ID)
            },
            "label_distribution": {
                "bia4_inside": int(df['label'].sum()),
                "not_bia4_inside": int(len(df) - df['label'].sum()),
                "ratio": float(df['label'].mean())
            },
            "image_sizes": {
                "widths": [img['width'] for img in coco_data['images']],
                "heights": [img['height'] for img in coco_data['images']]
            }
        }
        return report

class Bia4ModelTrainer:
    """Trainer for BIA4 classification model"""
    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.learn = None
        
    def create_data_loaders(self, df: pd.DataFrame) -> DataLoaders:
        """Create FastAI DataLoaders from DataFrame"""
        batch_tfms = aug_transforms(mult=1.5, max_rotate=15, max_zoom=1.1, max_warp=0.1)
        
        dblock = DataBlock(
            blocks=(ImageBlock, CategoryBlock),
            get_x=ColReader('image_path'),
            get_y=ColReader('label'),
            splitter=RandomSplitter(valid_pct=self.config.VALID_PCT, seed=self.config.SEED),
            item_tfms=Resize(self.config.IMG_SIZE),
            batch_tfms=batch_tfms
        )
        
        return dblock.dataloaders(df, bs=self.config.BATCH_SIZE)
    
    def create_learner(self, dls: DataLoaders, arch: callable = resnet50) -> None:
        """Create vision learner with specified architecture"""
        self.learn = vision_learner(
            dls, 
            arch, 
            pretrained=True, 
            metrics=[accuracy, error_rate]
        )
    
    def find_optimal_lr(self) -> float:
        """Find optimal learning rate"""
        if self.learn is None:
            raise ValueError("Learner not initialized. Call create_learner first.")
        
        lr_min = self.learn.lr_find()
        plt.show()
        return lr_min.valley
    
    def train(self, epochs: int, base_lr: Optional[float] = None) -> None:
        """Train the model"""
        if self.learn is None:
            raise ValueError("Learner not initialized.")
        
        if base_lr is None:
            base_lr = self.find_optimal_lr()
        
        self.learn.fine_tune(epochs, base_lr=base_lr)
    
    def evaluate(self) -> Tuple[float, float]:
        """Evaluate model performance"""
        if self.learn is None:
            raise ValueError("Learner not initialized.")
        
        return self.learn.validate()
    
    def save_model(self, path: Optional[str] = None) -> None:
        """Save trained model"""
        if path is None:
            path = self.config.MODEL_SAVE_PATH
        
        self.learn.export(path)
        print(f"Model saved to {path}")
    
    def load_model(self, path: Optional[str] = None) -> None:
        """Load trained model"""
        if path is None:
            path = self.config.MODEL_SAVE_PATH
        
        self.learn = load_learner(path)
        print(f"Model loaded from {path}")

class TimmModelWrapper:
    """Wrapper for TIMM models to work with FastAI"""
    def __init__(self, model_name: str, num_classes: int = 2, pretrained: bool = True):
        self.model_name = model_name
        self.num_classes = num_classes
        self.pretrained = pretrained
        
    def __call__(self):
        """Create and return the TIMM model"""
        model = create_model(
            self.model_name,
            pretrained=self.pretrained,
            num_classes=self.num_classes
        )
        return model

class AdvancedModelTrainer:
    """Trainer with support for multiple architectures and ensemble methods"""
    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.models = {}
        self.predictions = {}
        self.validation_results = {}
        
    def create_advanced_data_loaders(self, df: pd.DataFrame) -> DataLoaders:
        """Create DataLoaders with basic augmentation"""
        batch_tfms = [
            *aug_transforms(
                mult=2.0, 
                max_rotate=20, 
                max_zoom=1.2, 
                max_warp=0.15,
                max_lighting=0.4,
                p_affine=0.8,
                p_lighting=0.8
            )
        ]
        
        dblock = DataBlock(
            blocks=(ImageBlock, CategoryBlock),
            get_x=ColReader('image_path'),
            get_y=ColReader('label'),
            splitter=RandomSplitter(valid_pct=self.config.VALID_PCT, seed=self.config.SEED),
            item_tfms=[Resize(self.config.IMG_SIZE)],
            batch_tfms=batch_tfms
        )
        
        dls = dblock.dataloaders(df, bs=self.config.BATCH_SIZE)
        return dls
    
    def train_single_model(self, arch_name: str, dls: DataLoaders, save_model: bool = True) -> Tuple[Learner, Dict]:
        """Train a single model architecture"""
        print(f"\n=== Training {arch_name} ===")
        
        if arch_name in ['resnet50', 'resnet101']:
            arch = self.config.ARCHITECTURES[arch_name]
            learn = vision_learner(
                dls, 
                arch, 
                pretrained=True, 
                metrics=[accuracy, error_rate, F1Score()]
            )
        else:
            model_wrapper = TimmModelWrapper(
                self.config.ARCHITECTURES[arch_name],
                num_classes=len(dls.vocab)
            )
            learn = Learner(
                dls, 
                model_wrapper(), 
                metrics=[accuracy, error_rate, F1Score()]
            )
        
        print("Finding optimal learning rate...")
        with learn.no_bar():
            lr_min = learn.lr_find(show_plot=False)
        
        optimal_lr = lr_min.valley if hasattr(lr_min, 'valley') else 1e-3
        print(f"Optimal LR: {optimal_lr:.2e}")
        
        print("Stage 1: Initial training...")
        with learn.no_bar():
            if arch_name.startswith('vit') or arch_name.startswith('swin'):
                learn.freeze()
                learn.fit_one_cycle(
                    self.config.EPOCHS_STAGE1, 
                    slice(optimal_lr/10, optimal_lr)
                )
                learn.unfreeze()
                learn.fit_one_cycle(
                    self.config.EPOCHS_STAGE2, 
                    slice(optimal_lr/100, optimal_lr/10)
                )
            else:
                learn.fine_tune(
                    self.config.EPOCHS_STAGE1 + self.config.EPOCHS_STAGE2, 
                    base_lr=optimal_lr
                )
        
        results = self._evaluate_model(learn, arch_name)
        
        if save_model:
            model_path = Path(self.config.ENSEMBLE_MODELS_DIR) / f"{arch_name}_model.pkl"
            model_path.parent.mkdir(parents=True, exist_ok=True)
            learn.export(model_path)
            print(f"Model saved: {model_path}")
        
        self.models[arch_name] = learn
        self.validation_results[arch_name] = results
        
        return learn, results
    
    def _evaluate_model(self, learn: Learner, model_name: str) -> Dict:
        """Evaluate model"""
        val_dl = learn.dls.valid
        preds, targets = learn.get_preds(dl=val_dl)
        
        y_pred = preds.argmax(dim=1).numpy()
        y_true = targets.numpy()
        y_prob = preds.numpy()
        
        accuracy = (y_pred == y_true).mean()
        class_report = classification_report(
            y_true, y_pred, 
            target_names=['Not_Bia4_Inside', 'Bia4_Inside'],
            output_dict=True
        )
        
        results = {
            'accuracy': accuracy,
            'predictions': y_pred,
            'probabilities': y_prob,
            'targets': y_true,
            'classification_report': class_report,
            'confusion_matrix': confusion_matrix(y_true, y_pred)
        }
        
        print(f"\n{model_name} Results:")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"F1-Score: {class_report['weighted avg']['f1-score']:.4f}")
        
        return results
    
    def train_multiple_models(self, df: pd.DataFrame, architectures: List[str] = None) -> Dict:
        """Train multiple model architectures"""
        if architectures is None:
            architectures = ['resnet50', 'efficientnet_b0', 'vit_base_patch16_224']
        
        print(f"Training {len(architectures)} models...")
        results = {}
        
        for arch_name in architectures:
            try:
                dls = self.create_advanced_data_loaders(df)
                learn, model_results = self.train_single_model(arch_name, dls)
                results[arch_name] = model_results
                
                self.predictions[arch_name] = {
                    'probabilities': model_results['probabilities'],
                    'predictions': model_results['predictions'],
                    'targets': model_results['targets']
                }
                
                del learn
                torch.cuda.empty_cache() if torch.cuda.is_available() else None
                
            except Exception as e:
                print(f"Error training {arch_name}: {e}")
                continue
        
        self._save_ensemble_data()
        return results
    
    def _save_ensemble_data(self):
        """Save predictions for ensemble methods"""
        ensemble_data = {
            'predictions': self.predictions,
            'validation_results': self.validation_results,
            'config': {
                'architectures': list(self.predictions.keys()),
                'img_size': self.config.IMG_SIZE,
                'batch_size': self.config.BATCH_SIZE
            }
        }
        
        with open(self.config.ENSEMBLE_PREDICTIONS_PATH, 'wb') as f:
            pickle.dump(ensemble_data, f)
        
        print(f"Ensemble data saved: {self.config.ENSEMBLE_PREDICTIONS_PATH}")

class EnsembleMethod:
    """Ensemble methods for combining multiple models"""
    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.ensemble_data = None
    
    def load_ensemble_data(self) -> Dict:
        """Load saved ensemble predictions"""
        with open(self.config.ENSEMBLE_PREDICTIONS_PATH, 'rb') as f:
            self.ensemble_data = pickle.load(f)
        return self.ensemble_data
    
    def simple_average_ensemble(self) -> Tuple[np.ndarray, float]:
        """Simple averaging ensemble"""
        if self.ensemble_data is None:
            self.load_ensemble_data()
        
        predictions = self.ensemble_data['predictions']
        all_probs = []
        targets = None
        
        for model_name, pred_data in predictions.items():
            all_probs.append(pred_data['probabilities'])
            if targets is None:
                targets = pred_data['targets']
        
        ensemble_probs = np.mean(all_probs, axis=0)
        ensemble_preds = ensemble_probs.argmax(axis=1)
        accuracy = (ensemble_preds == targets).mean()
        
        print(f"Simple Average Ensemble Accuracy: {accuracy:.4f}")
        return ensemble_preds, accuracy
    
    def weighted_ensemble(self, weights: Optional[List[float]] = None) -> Tuple[np.ndarray, float]:
        """Weighted ensemble based on model performance"""
        if self.ensemble_data is None:
            self.load_ensemble_data()
        
        predictions = self.ensemble_data['predictions']
        val_results = self.ensemble_data['validation_results']
        
        if weights is None:
            weights = [val_results[model_name]['accuracy'] for model_name in predictions.keys()]
            weights = np.array(weights) / np.sum(weights)
        
        print(f"Model weights: {dict(zip(predictions.keys(), weights))}")
        
        all_probs = []
        targets = None
        
        for i, (model_name, pred_data) in enumerate(predictions.items()):
            weighted_probs = pred_data['probabilities'] * weights[i]
            all_probs.append(weighted_probs)
            if targets is None:
                targets = pred_data['targets']
        
        ensemble_probs = np.sum(all_probs, axis=0)
        ensemble_preds = ensemble_probs.argmax(axis=1)
        accuracy = (ensemble_preds == targets).mean()
        print(f"Weighted Ensemble Accuracy: {accuracy:.4f}")
        return ensemble_preds, accuracy
    
    def voting_ensemble(self, voting_type: str = 'soft') -> Tuple[np.ndarray, float]:
        """Voting ensemble (hard or soft)"""
        if self.ensemble_data is None:
            self.load_ensemble_data()
        
        predictions = self.ensemble_data['predictions']
        
        if voting_type == 'hard':
            all_preds = []
            targets = None
            for model_name, pred_data in predictions.items():
                all_preds.append(pred_data['predictions'])
                if targets is None:
                    targets = pred_data['targets']
            
            votes = np.array(all_preds).T
            ensemble_preds = np.array([1 if np.sum(sample_votes) > len(sample_votes) / 2 else 0 for sample_votes in votes])
        else:
            ensemble_preds, _ = self.simple_average_ensemble()
            targets = list(predictions.values())[0]['targets']
        
        accuracy = (ensemble_preds == targets).mean()
        print(f"{voting_type.title()} Voting Ensemble Accuracy: {accuracy:.4f}")
        return ensemble_preds, accuracy

class ModelAnalyzer:
    """Analysis and visualization for trained models"""
    def __init__(self, config: UnifiedConfig):
        self.config = config
    
    def compare_models(self, validation_results: Dict) -> pd.DataFrame:
        """Compare performance across models"""
        comparison_data = []
        for model_name, results in validation_results.items():
            class_report = results['classification_report']
            comparison_data.append({
                'Model': model_name,
                'Accuracy': results['accuracy'],
                'F1_Score': class_report['weighted avg']['f1-score'],
                'Precision': class_report['weighted avg']['precision'],
                'Recall': class_report['weighted avg']['recall'],
                'Bia4_Inside_F1': class_report.get('1', {}).get('f1-score', 0),
                'Not_Bia4_Inside_F1': class_report.get('0', {}).get('f1-score', 0)
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        if len(df_comparison) > 0 and 'Accuracy' in df_comparison.columns:
            df_comparison = df_comparison.sort_values('Accuracy', ascending=False)
        
        print("=== Model Performance Comparison ===")
        if len(df_comparison) > 0:
            print(df_comparison.round(4).to_string(index=False))
        else:
            print("No validation results available.")
        return df_comparison
    
    def plot_model_comparison(self, df_comparison: pd.DataFrame) -> Optional[plt.Figure]:
        """Visualize model comparison"""
        if len(df_comparison) == 0:
            print("No data to plot.")
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        if 'Accuracy' in df_comparison.columns:
            axes[0, 0].bar(df_comparison['Model'], df_comparison['Accuracy'])
            axes[0, 0].set_title('Model Accuracy Comparison')
            axes[0, 0].set_ylabel('Accuracy')
            axes[0, 0].tick_params(axis='x', rotation=45)
        
        if 'F1_Score' in df_comparison.columns:
            axes[0, 1].bar(df_comparison['Model'], df_comparison['F1_Score'])
            axes[0, 1].set_title('F1 Score Comparison')
            axes[0, 1].set_ylabel('F1 Score')
            axes[0, 1].tick_params(axis='x', rotation=45)
        
        if 'Bia4_Inside_F1' in df_comparison.columns and 'Not_Bia4_Inside_F1' in df_comparison.columns:
            x = np.arange(len(df_comparison))
            width = 0.35
            axes[1, 0].bar(x - width/2, df_comparison['Bia4_Inside_F1'], width, label='Bia4_Inside', alpha=0.7)
            axes[1, 0].bar(x + width/2, df_comparison['Not_Bia4_Inside_F1'], width, label='Not_Bia4_Inside', alpha=0.7)
            axes[1, 0].set_title('Class-specific F1 Scores')
            axes[1, 0].set_ylabel('F1 Score')
            axes[1, 0].set_xticks(x)
            axes[1, 0].set_xticklabels(df_comparison['Model'], rotation=45)
            axes[1, 0].legend()
        
        if 'Precision' in df_comparison.columns and 'Recall' in df_comparison.columns:
            axes[1, 1].scatter(df_comparison['Precision'], df_comparison['Recall'])
            for i, model in enumerate(df_comparison['Model']):
                axes[1, 1].annotate(model, (df_comparison['Precision'].iloc[i], df_comparison['Recall'].iloc[i]))
            axes[1, 1].set_title('Precision vs Recall')
            axes[1, 1].set_xlabel('Precision')
            axes[1, 1].set_ylabel('Recall')
        
        plt.tight_layout()
        plt.show()
        return fig
    
    def plot_confusion_matrices(self, validation_results: Dict) -> Optional[plt.Figure]:
        """Plot confusion matrices for all models"""
        n_models = len(validation_results)
        if n_models == 0:
            print("No validation results to plot.")
            return None
        
        cols = min(3, n_models)
        rows = (n_models + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))
        if n_models == 1:
            axes = [axes]
        elif rows == 1:
            axes = axes.reshape(1, -1)
        
        for idx, (model_name, results) in enumerate(validation_results.items()):
            row = idx // cols
            col = idx % cols
            ax = axes[row, col] if rows > 1 else axes[col]
            
            cm = results['confusion_matrix']
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                       xticklabels=['Not_Bia4_Inside', 'Bia4_Inside'],
                       yticklabels=['Not_Bia4_Inside', 'Bia4_Inside'])
            ax.set_title(f'{model_name} Confusion Matrix')
            ax.set_ylabel('True Label')
            ax.set_xlabel('Predicted Label')
        
        for idx in range(n_models, rows * cols):
            row = idx // cols
            col = idx % cols
            if rows > 1:
                axes[row, col].set_visible(False)
            else:
                axes[col].set_visible(False)
        
        plt.tight_layout()
        plt.show()
        return fig

class AdvancedBia4Pipeline:
    """Complete pipeline for advanced BIA4 classification"""
    def __init__(self, config: UnifiedConfig = None):
        self.config = config or UnifiedConfig(advanced=True)
        self.processor = CocoDataProcessor(self.config)
        self.trainer = AdvancedModelTrainer(self.config)
        self.ensemble = EnsembleMethod(self.config)
        self.analyzer = ModelAnalyzer(self.config)
    
    def run_complete_pipeline(self, df: pd.DataFrame, architectures: List[str] = None, use_ensemble: bool = True) -> Dict[str, Any]:
        """Run complete training pipeline"""
        print("=== Starting Advanced BIA4 Classification Pipeline ===")
        
        set_random_seeds(self.config.SEED)
        
        architectures = architectures or ['resnet50', 'efficientnet_b0', 'vit_base_patch16_224']
        print(f"\n1. Training {len(architectures)} architectures...")
        validation_results = self.trainer.train_multiple_models(df, architectures)
        
        if not validation_results:
            print("No models were trained successfully!")
            return {'individual_results': {}, 'comparison_df': pd.DataFrame(), 'ensemble_results': None}
        
        print("\n2. Comparing individual model performance...")
        df_comparison = self.analyzer.compare_models(validation_results)
        self.analyzer.plot_model_comparison(df_comparison)
        self.analyzer.plot_confusion_matrices(validation_results)
        
        ensemble_results = None
        if use_ensemble and len(validation_results) > 1:
            print("\n3. Creating ensemble models...")
            try:
                avg_preds, avg_acc = self.ensemble.simple_average_ensemble()
                weighted_preds, weighted_acc = self.ensemble.weighted_ensemble()
                soft_preds, soft_acc = self.ensemble.voting_ensemble('soft')
                hard_preds, hard_acc = self.ensemble.voting_ensemble('hard')
                
                print(f"\n=== Ensemble Results Summary ===")
                print(f"Simple Average: {avg_acc:.4f}")
                print(f"Weighted Average: {weighted_acc:.4f}")
                print(f"Soft Voting: {soft_acc:.4f}")
                print(f"Hard Voting: {hard_acc:.4f}")
                
                ensemble_results = {
                    'simple_average': avg_acc,
                    'weighted_average': weighted_acc,
                    'soft_voting': soft_acc,
                    'hard_voting': hard_acc
                }
            except Exception as e:
                print(f"Error in ensemble methods: {e}")
                print("Skipping ensemble evaluation...")
        
        if validation_results:
            best_individual = max(validation_results.items(), key=lambda x: x[1]['accuracy'])
            print(f"Best Individual Model: {best_individual[0]} ({best_individual[1]['accuracy']:.4f})")
        
        return {
            'individual_results': validation_results,
            'comparison_df': df_comparison,
            'ensemble_results': ensemble_results
        }

def train_and_evaluate_single_model(config: UnifiedConfig, df: pd.DataFrame, display_mode: str = "auto") -> Dict[str, Any]:
    """Train and evaluate a single model"""
    trainer = Bia4ModelTrainer(config)
    dls = trainer.create_data_loaders(df)
    
    print("Creating data loaders...")
    dls.show_batch(max_n=4, figsize=(10, 5))
    
    print("Initializing model...")
    trainer.create_learner(dls, resnet50)
    
    print("First training round...")
    trainer.train(epochs=4, base_lr=1e-3)
    
    print("Second training round...")
    trainer.train(epochs=8)
    
    val_loss, val_accuracy = trainer.evaluate()
    print(f"Final validation - Loss: {val_loss:.4f}, Accuracy: {val_accuracy:.4f}")
    
    trainer.save_model()
    trainer.learn.show_results(max_n=4)
    
    return {
        'trainer': trainer,
        'validation': {'loss': val_loss, 'accuracy': val_accuracy}
    }

def main_pipeline(coco_json_path: str = None, 
                 base_image_dir: str = None, 
                 model_save_path: str = None,
                 display_mode: str = "auto") -> Dict[str, Any]:
    """Main execution pipeline for single model training"""
    config = UnifiedConfig(base_image_dir)
    
    if coco_json_path:
        config.COCO_JSON_PATH = Path(coco_json_path).resolve()
    if base_image_dir:
        config.AUGMENTED_DIR = Path(base_image_dir).resolve() / 'augmented'
    if model_save_path:
        config.MODEL_SAVE_PATH = Path(model_save_path).resolve()
    
    set_random_seeds(config.SEED)
    
    # Load and augment data
    df_combined, merged_coco = load_and_augment_data(config, coco_json_path, base_image_dir)
    
    # Analyze dataset
    processor = CocoDataProcessor(config)
    analyzer = DatasetAnalyzer(processor, display_mode=display_mode)
    dataset_report = analyzer.analyze_dataset(merged_coco)
    analyzer.plot_label_distribution(df_combined)
    
    # Train and evaluate model
    training_results = train_and_evaluate_single_model(config, df_combined, display_mode)
    
    # Predict on sample image
    example_image = Path(config.BASE_DIR) / 'bia4 (714).bmp'
    sample_prediction = None
    if example_image.exists():
        prediction, confidence = predict_single_image(
            training_results['trainer'].config.MODEL_SAVE_PATH, str(example_image))
        sample_prediction = {'image_path': str(example_image), 'prediction': prediction, 'confidence': confidence}
        print(f"Example prediction: {prediction}, Confidence: {confidence:.4f}")
    
    return {
        'dataset': df_combined,
        'coco_data': merged_coco,
        'dataset_report': dataset_report,
        'training_results': training_results,
        'sample_prediction': sample_prediction
    }

def main_advanced_pipeline(coco_json_path: str = None, 
                          base_image_dir: str = None, 
                          model_save_path: str = None,
                          architectures: List[str] = None) -> Dict[str, Any]:
    """Main execution pipeline for advanced models with functional approach"""
    config = UnifiedConfig(base_image_dir, advanced=True)
    if coco_json_path:
        config.COCO_JSON_PATH = Path(coco_json_path).resolve()
    if base_image_dir:
        config.AUGMENTED_DIR = Path(base_image_dir).resolve() / 'augmented'
    if model_save_path:
        config.MODEL_SAVE_PATH = Path(model_save_path).resolve()
    
    set_random_seeds(config.SEED)

    # Load and augment data
    df_combined, merged_coco = load_and_augment_data(config, coco_json_path, base_image_dir)

    # Analyze dataset
    processor = CocoDataProcessor(config)
    analyzer = DatasetAnalyzer(processor)
    dataset_report = analyzer.analyze_dataset(merged_coco)
    analyzer.plot_label_distribution(df_combined)

    # Initialize pipeline
    pipeline = AdvancedBia4Pipeline(config)
    architectures = architectures or ['resnet50', 'efficientnet_b0', 'vit_base_patch16_224']
    
    # Run training pipeline
    pipeline_results = pipeline.run_complete_pipeline(df_combined, architectures=architectures, use_ensemble=True)

    # Predict and visualize for a sample image
    sample_image = '/content/bia4 (715).bmp'
    sample_prediction = None
    if Path(sample_image).exists():
        predictions, center = predict_and_visualize(config, architectures, sample_image)
        sample_prediction = {'image_path': sample_image, 'predictions': predictions, 'center': center}
        print(f"Sample prediction results: {predictions}, Center: {center}")

    return {
        'dataset': df_combined,
        'coco_data': merged_coco,
        'dataset_report': dataset_report,
        'pipeline_results': pipeline_results,
        'sample_prediction': sample_prediction
    }

def predict_single_image(model_path: str, image_path: str) -> Tuple[str, float]:
    """Make prediction on a single image"""
    learn = load_learner(model_path)
    pred, pred_idx, probs = learn.predict(image_path)
    return pred, probs[pred_idx].item()

def batch_predict(model_path: str, image_paths: List[str]) -> List[Tuple[str, float]]:
    """Make predictions on a batch of images"""
    learn = load_learner(model_path)
    test_dl = learn.dls.test_dl(image_paths)
    preds, _ = learn.get_preds(dl=test_dl)
    
    results = []
    for pred in preds:
        pred_label = learn.dls.vocab[pred.argmax()]
        confidence = pred.max().item()
        results.append((pred_label, confidence))
    
    return results

if __name__ == "__main__":
    coco_json_path = UnifiedConfig().COCO_JSON_PATH
    base_image_dir = str(UnifiedConfig().BASE_DIR)
    model_save_path = UnifiedConfig().MODEL_SAVE_PATH
    
    # Run main pipeline
    results = main_pipeline(
        coco_json_path=coco_json_path,
        base_image_dir=base_image_dir,
        model_save_path=model_save_path
    )
    
    # Run advanced pipeline
    advanced_results = main_advanced_pipeline(
        coco_json_path=coco_json_path,
        base_image_dir=base_image_dir,
        model_save_path=model_save_path
    )