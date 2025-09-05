import torch
import importlib

class DeepfakeDetector:
    def __init__(self, model_name="resnet_inception", confidence_threshold=0.5, device=None):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.device = device if device else torch.device("cpu")

        # Map model names to detector module paths and class names
        self.detector_info = {
            "resnet_inception": ("mukh.deepfake_detection.models.resnet_inception.resnet_inception_detector", "ResNetInceptionDetector"),
            # Add other models here if available, e.g.:
            # "efficientnet": ("mukh.deepfake_detection.models.efficientnet.efficientnet_detector", "EfficientNetDetector"),
        }

        if model_name not in self.detector_info:
            raise ValueError(f"Unsupported model_name: {model_name}")

        module_name, class_name = self.detector_info[model_name]
        module = importlib.import_module(module_name)
        detector_class = getattr(module, class_name)

        self.detector = detector_class(
            confidence_threshold=confidence_threshold,
            device=device
        )

    def detect(self, media_path, save_csv=False, csv_path=None, save_annotated=False, output_folder=None, num_frames=1):
        print(f"Detecting deepfake in {media_path} using model {self.model_name} on device {self.device}")
        # Determine if media is image or video by extension
        ext = media_path.split('.')[-1].lower()
        image_exts = {"jpg", "jpeg", "png", "bmp", "gif"}
        video_exts = {"mp4", "avi", "mov", "mkv"}

        if ext in image_exts:
            detection = self.detector.detect_image(
                image_path=media_path,
                save_csv=save_csv,
                csv_path=csv_path,
                save_annotated=save_annotated,
                output_folder=output_folder
            )
            # detect_image returns (DeepfakeDetection, is_deepfake)
            detections = [detection[0]]
            final_result = "Deepfake" if detection[1] else "Real"
        elif ext in video_exts:
            detections, final_result = self.detector.detect_video(
                video_path=media_path,
                save_csv=save_csv,
                csv_path=csv_path,
                save_annotated=save_annotated,
                output_folder=output_folder,
                num_frames=num_frames
            )
        else:
            raise ValueError(f"Unsupported media file extension: {ext}")

        return detections, final_result
