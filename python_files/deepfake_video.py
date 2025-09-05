import torch
from python_files.deepfake_detector import DeepfakeDetector

def deepfake_video(video_path, confidence_threshold=0.5, num_frames=11):

    """
    Detect deepfake in a video using ResNetInception model.
    Returns the final result string and the confidence score (0-100).
    Uses majority voting and average confidence for robust results.
    """
    # Use more frames and a stricter threshold for better accuracy
    confidence_threshold = 0.7
    num_frames = 25
    detector = DeepfakeDetector(
        model_name="resnet_inception",
        confidence_threshold=confidence_threshold,
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    )
    detections, final_result = detector.detect(
        media_path=video_path,
        save_csv=False,
        save_annotated=False,
        output_folder=None,
        num_frames=num_frames
    )
    if not detections or not isinstance(detections, list) or len(detections) == 0:
        # fallback to final_result if no detections
        if isinstance(final_result, bool):
            result = 'Deepfake or AI Generated' if final_result else 'Real'
        else:
            result = 'Deepfake or AI Generated' if str(final_result).lower() == 'deepfake' else 'Real'
        return result, 0.0

    # Majority voting and average confidence
    deepfake_count = 0
    real_count = 0
    confidences = []
    for detection in detections:
        is_deepfake = False
        if hasattr(detection, 'is_deepfake'):
            is_deepfake = detection.is_deepfake
        elif hasattr(detection, 'label'):
            is_deepfake = str(detection.label).lower() == 'deepfake'
        elif hasattr(detection, 'prediction'):
            is_deepfake = str(detection.prediction).lower() == 'deepfake'
        if is_deepfake:
            deepfake_count += 1
        else:
            real_count += 1
        if hasattr(detection, 'confidence'):
            confidences.append(detection.confidence)

    total = deepfake_count + real_count
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
    # Only return 'Real' or 'Deepfake or AI Generated'
    if deepfake_count > real_count and avg_conf >= confidence_threshold:
        result = 'Deepfake or AI Generated'
        confidence = avg_conf
    else:
        result = 'Real'
        confidence = 1 - avg_conf if avg_conf > 0 else 1.0
    return result, round(confidence * 100, 2)
