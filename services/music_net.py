import os
import tempfile

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import librosa
import torch
import mlflow.pytorch
from torchvision import transforms

from core.config import DEFAULT_SETTINGS


MAPPING_DICT_MUSIC_NET = {
    'blues': 0, 'chanson': 1, 'classical': 2, 'country': 3, 'dance': 4, 'dub': 5,
    'electro': 6, 'folk': 7, 'funk': 8, 'hard rock': 9, 'hip-hop': 10, 'house': 11,
    'jazz': 12, 'metal': 13, 'pop': 14, 'rap': 15, 'reggae': 16, 'rock': 17,
}


def create_preprocessed_spectrogram(audio_path, sr=22050, n_mels=128, fmax=8000, img_size=(224, 224), start_time=20, segment_duration=20):
    try:
        # Load the audio file
        y, sr = librosa.load(audio_path, sr=sr, offset=start_time, duration=segment_duration)
        
        # Generate the spectrogram
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, fmax=fmax)
        S_DB = librosa.power_to_db(S, ref=np.max)
        
        # Plot the spectrogram
        plt.figure(figsize=(10, 4))
        plt.axis('off')
        librosa.display.specshow(S_DB, sr=sr, x_axis=None, y_axis=None, fmax=fmax)
        
        # Save the plot to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
            plt.savefig(tmpfile.name, bbox_inches='tight', pad_inches=0)
            plt.close()
            
            # Open the image and resize it
            img = Image.open(tmpfile.name).convert('RGB')  # Convert to RGB
            img = img.resize(img_size, Image.Resampling.LANCZOS)
            os.remove(tmpfile.name)
        
        # Transform the image to tensor
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])
        img_tensor = transform(img).unsqueeze(0)  # Add batch dimension
        
        return img_tensor
    except Exception as e:
        print(f"Error processing {audio_path}: {e}")
        return None
    

def get_production_model():
    # load the model using mlflow
    minio_url = F"s3://{DEFAULT_SETTINGS.minio_music_net_bucket_name}/data/"

    os.environ["AWS_ACCESS_KEY_ID"] = DEFAULT_SETTINGS.minio_root_user
    os.environ["AWS_SECRET_ACCESS_KEY"] = DEFAULT_SETTINGS.minio_root_password
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = f"http://{DEFAULT_SETTINGS.minio_endpoint}" 

    # Check if CUDA is available
    if torch.cuda.is_available():
        return mlflow.pytorch.load_model(minio_url)
    else:
        return mlflow.pytorch.load_model(minio_url, map_location=torch.device('cpu'))


def predict_with_production_music_net(model, img_tensor):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    img_tensor = img_tensor.to(device)
    model.eval()
    with torch.no_grad():
        output = model(img_tensor)
        _, predicted = torch.max(output, 1)
    
    idx_to_class = {v: k for k, v in MAPPING_DICT_MUSIC_NET.items()}
    predicted_class_name = idx_to_class[predicted.item()]

    return predicted_class_name


