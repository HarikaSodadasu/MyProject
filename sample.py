import torch
import open_clip
from PIL import Image
import time
import cv2

# Load CLIP model
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model, preprocess, tokenizer = open_clip.create_model_and_transforms(
    'ViT-L-14-quickgelu', pretrained='openai'
)
model = model.to(device)
model.eval()

# Load a sample image (replace with your frame)

try:
    dummy_frame = torch.rand(3, 224, 224)  # Use rand, not randn for valid image data
    image_array = (dummy_frame.permute(1, 2, 0) * 255).byte().cpu().numpy()
    image = Image.fromarray(image_array)
except Exception as e:
    print(f"Error creating dummy image: {e}")
    exit()
preprocessed_image = preprocess(image).unsqueeze(0).to(device)

with torch.no_grad():
    start_time = time.time()
    if device == 'cuda':
        torch.cuda.synchronize()
    image_features = model.encode_image(preprocessed_image)
    if device == 'cuda':
        torch.cuda.synchronize()
    end_time = time.time()
    inference_time_ms = (end_time - start_time) * 1000

print(f"Inference time for one frame: {inference_time_ms:.2f} ms")