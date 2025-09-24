"""
BIA4 Image Classification Pipeline
Refactored version with functional programming principles and clean code practices
"""

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

os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'


# Configuration
class Config:
    """Configuration class for all paths and parameters"""
    SEED = 42
    IMG_SIZE = 224
    BATCH_SIZE = 32
    VALID_PCT = 0.2
    
    # Paths (using absolute paths)
    BASE_DIR = Path(__file__).parent.parent.resolve() / 'datasets' / 'bia4'
    COCO_JSON_PATH = str(BASE_DIR / 'All-Coco-3.json')
    AUGMENTED_DIR = str(BASE_DIR / 'augmented')
    AUGMENTED_JSON_PATH = str(BASE_DIR / 'augmented' / 'augmented_coco.json')
    MERGED_JSON_PATH = str(BASE_DIR / 'All-Coco-3-merged.json')
    MODEL_SAVE_PATH = str(BASE_DIR / 'models' / 'bia4_inside_model.pkl')

    # Category ID for Bia4_Inside
    BIA4_INSIDE_CATEGORY_ID = 3

# Set random seeds for reproducibility
def set_random_seeds(seed: int = Config.SEED) -> None:
    """Set random seeds for reproducibility"""
    set_seed(seed, reproducible=True)
    torch.manual_seed(seed)
    np.random.seed(seed)

class CocoDataProcessor:
    """Processor for COCO format dataset operations"""
    
    def __init__(self, config: Config):
        self.config = config
        self.coco_data = None
        self.base_image_dir = None
    
    def load_coco_data(self, json_path: str, base_image_dir: str = None) -> Dict[str, Any]:
        """Load COCO JSON data with flexible image path"""
        self.base_image_dir = Path(base_image_dir).resolve() if base_image_dir else Path(json_path).parent.resolve()
        with open(json_path, 'r') as f:
            return json.load(f)
    
    def save_coco_data(self, data: Dict[str, Any], output_path: str) -> None:
        """Save COCO JSON data"""
        os.makedirs(Path(output_path).parent, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def point_in_bbox(self, point: Tuple[float, float], bbox: List[float]) -> bool:
        """Check if a point is inside a bounding box"""
        x, y = point
        x_min, y_min, width, height = bbox
        return (x_min <= x <= x_min + width and 
                y_min <= y <= y_min + height)
    
    def get_image_center(self, image_info: Dict) -> Tuple[float, float]:
        """Get center point of an image"""
        return (image_info['width'] / 2, image_info['height'] / 2)

class Bia4DatasetBuilder:
    """Builder for BIA4 classification dataset"""
    
    def __init__(self, processor: CocoDataProcessor):
        self.processor = processor
        self.config = processor.config
        self._annotations_by_image = None
        self._bia4_annotations_by_image = None
    
    @property
    def base_image_dir(self) -> Path:
        """Get base image directory from processor or config"""
        if hasattr(self.processor, 'base_image_dir') and self.processor.base_image_dir:
            return Path(self.processor.base_image_dir).resolve()
        return Path(self.config.COCO_JSON_PATH).parent.resolve()
    
    def _build_annotations_index(self, annotations: List[Dict]) -> Tuple[Dict, Dict]:
        """Build optimized indexes for faster lookup"""
        annotations_by_image = {}
        bia4_annotations_by_image = {}
        
        for ann in annotations:
            image_id = ann['image_id']
            
            # Index for all annotations
            if image_id not in annotations_by_image:
                annotations_by_image[image_id] = []
            annotations_by_image[image_id].append(ann)
            
            # Special index only for Bia4_Inside annotations
            if ann['category_id'] == self.config.BIA4_INSIDE_CATEGORY_ID:
                if image_id not in bia4_annotations_by_image:
                    bia4_annotations_by_image[image_id] = []
                bia4_annotations_by_image[image_id].append(ann)
        
        return annotations_by_image, bia4_annotations_by_image
    
    def _is_bia4_inside_center(self, 
                             image_id: int, 
                             center_point: Tuple[float, float], 
                             annotations: List[Dict]) -> bool:
        """Ultra-optimized version with specialized indexing"""
        if self._annotations_by_image is None or self._bia4_annotations_by_image is None:
            self._annotations_by_image, self._bia4_annotations_by_image = \
                self._build_annotations_index(annotations)
        
        if image_id not in self._bia4_annotations_by_image:
            return False
        
        bia4_annotations = self._bia4_annotations_by_image[image_id]
        return any(
            self.processor.point_in_bbox(center_point, ann['bbox'])
            for ann in bia4_annotations
        )
    
    def create_label_dataframe(self, coco_data: Dict[str, Any]) -> pd.DataFrame:
        """Create DataFrame with image paths and labels"""
        data = []
        
        self._build_annotations_index(coco_data['annotations'])
        
        for img in coco_data['images']:
            img_id = img['id']
            img_path = self.base_image_dir / img['file_name']
            img_center = self.processor.get_image_center(img)
            
            label = self._is_bia4_inside_center(img_id, img_center, coco_data['annotations'])
            data.append([str(img_path), label])
        
        return pd.DataFrame(data, columns=['image_path', 'label'])

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
    
    def analyze_dataset(self, coco_data: Dict[str, Any]) -> None:
        """Print comprehensive dataset statistics"""
        categories = {cat['id']: cat['name'] for cat in coco_data['categories']}
        bia4_count = sum(1 for ann in coco_data['annotations'] 
                        if ann['category_id'] == self.processor.config.BIA4_INSIDE_CATEGORY_ID)
        
        print("=== Dataset Analysis ===")
        print(f"Images: {len(coco_data['images'])}")
        print(f"Annotations: {len(coco_data['annotations'])}")
        print(f"Bia4_Inside annotations: {bia4_count}")
        print(f"Categories: {categories}")
        
        widths = [img['width'] for img in coco_data['images']]
        heights = [img['height'] for img in coco_data['images']]
        print(f"Image size range: {min(widths)}-{max(widths)} x {min(heights)}-{max(heights)}")
        
        self._detailed_analysis(coco_data)
    
    def _detailed_analysis(self, coco_data: Dict[str, Any]) -> None:
        """Detailed dataset analysis"""
        category_counts = {}
        for ann in coco_data['annotations']:
            cat_id = ann['category_id']
            category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
        
        print("\n=== Category Distribution ===")
        for cat in coco_data['categories']:
            count = category_counts.get(cat['id'], 0)
            print(f"{cat['name']}: {count} annotations")
    
    def plot_label_distribution(self, df: pd.DataFrame, show_plot: bool = True) -> None:
        """Plot distribution of labels"""
        label_counts = df['label'].value_counts()
        
        if self.display_mode == "console":
            self._plot_console(label_counts)
        else:
            self._plot_notebook(label_counts, show_plot)
    
    def _plot_console(self, label_counts: pd.Series) -> None:
        """Display text-based plot in console"""
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
    
    def _plot_notebook(self, label_counts: pd.Series, show_plot: bool = True) -> None:
        """Display matplotlib plot in notebook"""
        plt.figure(figsize=(8, 5))
        
        plt.subplot(1, 2, 1)
        label_counts.plot(kind='bar', color=['#1f77b4', '#ff7f0e'])
        plt.title('Bia4_Inside Label Distribution')
        plt.xlabel('Label')
        plt.ylabel('Count')
        plt.xticks([0, 1], ['Not Bia4_Inside', 'Bia4_Inside'], rotation=45)
        
        plt.subplot(1, 2, 2)
        plt.pie(label_counts.values, labels=label_counts.index, 
                autopct='%1.1f%%', colors=['#1f77b4', '#ff7f0e'])
        plt.title('Label Proportion')
        
        plt.tight_layout()
        if show_plot:
            plt.show()
        else:
            return plt.gcf()
    
    def plot_image_size_distribution(self, coco_data: Dict[str, Any]) -> None:
        """Image size distribution"""
        widths = [img['width'] for img in coco_data['images']]
        heights = [img['height'] for img in coco_data['images']]
        
        if self.display_mode == "console":
            print(f"\n=== Image Size Distribution ===")
            print(f"Width: min={min(widths)}, max={max(widths)}, mean={np.mean(widths):.1f}")
            print(f"Height: min={min(heights)}, max={max(heights)}, mean={np.mean(heights):.1f}")
        else:
            plt.figure(figsize=(10, 4))
            
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
    
    def __init__(self, config: Config):
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

def main_pipeline(coco_json_path: str = None, 
                 base_image_dir: str = None, 
                 model_save_path: str = None,
                 display_mode: str = "auto"):
    """Main execution pipeline"""
    config = Config()
    
    if coco_json_path:
        config.COCO_JSON_PATH = Path(coco_json_path).resolve()
    if base_image_dir:
        config.AUGMENTED_DIR = Path(base_image_dir).resolve() / 'augmented'
    if model_save_path:
        config.MODEL_SAVE_PATH = Path(model_save_path).resolve()
    
    set_random_seeds(config.SEED)
    
    processor = CocoDataProcessor(config)
    dataset_builder = Bia4DatasetBuilder(processor)
    augmenter = Bia4Augmenter(processor)
    analyzer = DatasetAnalyzer(processor, display_mode=display_mode)
    trainer = Bia4ModelTrainer(config)
    
    print("Loading COCO data...")
    coco_data = processor.load_coco_data(config.COCO_JSON_PATH, base_image_dir)
    
    print("Creating base dataset...")
    df_base = dataset_builder.create_label_dataframe(coco_data)
    analyzer.analyze_dataset(coco_data)
    analyzer.plot_label_distribution(df_base)
    
    print("Handling augmented dataset...")
    aug_json_path = Path(config.AUGMENTED_JSON_PATH)
    if aug_json_path.exists():
        print("Loading existing augmented data...")
        aug_data = processor.load_coco_data(str(aug_json_path), base_image_dir=str(config.AUGMENTED_DIR))
        df_aug = dataset_builder.create_label_dataframe(aug_data)
        aug_json = aug_data
    else:
        print("Performing data augmentation...")
        df_aug, aug_json = augmenter.augment_dataset(coco_data)
        processor.save_coco_data(aug_json, config.AUGMENTED_JSON_PATH)
    
    merged_coco = coco_data.copy()
    merged_coco['images'].extend(aug_json['images'])
    merged_coco['annotations'].extend(aug_json['annotations'])
    processor.save_coco_data(merged_coco, config.MERGED_JSON_PATH)
    
    df_combined = pd.concat([df_base, df_aug], ignore_index=True)
    print(f"Combined dataset size: {len(df_combined)}")
    analyzer.plot_label_distribution(df_combined)
    
    print("Creating data loaders...")
    dls = trainer.create_data_loaders(df_combined)
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
    
    return trainer


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
    coco_json_path = Config.COCO_JSON_PATH
    base_image_dir = str(Config.BASE_DIR)
    model_save_path = Config.MODEL_SAVE_PATH
    
    trained_trainer = main_pipeline(
        coco_json_path=coco_json_path,
        base_image_dir=base_image_dir,
        model_save_path=model_save_path
    )
    
    example_image = Path(base_image_dir) / 'bia4 (887).bmp'
    if example_image.exists():
        prediction, confidence = predict_single_image(
            trained_trainer.config.MODEL_SAVE_PATH, str(example_image))
        print(f"Example prediction: {prediction}, Confidence: {confidence:.4f}")