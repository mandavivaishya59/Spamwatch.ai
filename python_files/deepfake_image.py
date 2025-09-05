import torch
from python_files.deepfake_detector import DeepfakeDetector

def deepfake_image(image_path, confidence_threshold=0.5, num_frames=1):

    """
    Detect deepfake in an image using ResNetInception model.
    Returns the final result string and the confidence score (0-100).
    Uses confidence threshold and returns 'Uncertain' if confidence is low.
    """
    detector = DeepfakeDetector(
        model_name="resnet_inception",
        confidence_threshold=confidence_threshold,
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    )

    detections, final_result = detector.detect(
        media_path=image_path,
        save_csv=False,
        save_annotated=False,
        output_folder=None,
        num_frames=num_frames
    )

    confidence = 0.0
    if detections and isinstance(detections, list) and len(detections) > 0:
        # For images, detections is a list with one DeepfakeDetection object
        detection = detections[0]
        if hasattr(detection, 'confidence'):
            confidence = detection.confidence
        # Use confidence threshold for decision
        if confidence >= confidence_threshold:
            result = 'Deepfake or AI Generated'
        else:
            result = 'Real'
            confidence = 1 - confidence if confidence > 0 else 1.0
    else:
        # fallback to final_result if no detection object
        if isinstance(final_result, bool):
            result = 'Deepfake or AI Generated' if final_result else 'Real'
        else:
            result = 'Deepfake or AI Generated' if str(final_result).lower() == 'deepfake' else 'Real'
    return result, round(confidence * 100, 2)

