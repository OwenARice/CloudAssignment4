from flask import Flask, request, jsonify
import torch
from torchvision import models, transforms
from PIL import Image
import io

# Load the pre-trained ResNet model
model = models.resnet18(pretrained=True)
model.eval()

app = Flask(__name__)

# Image transformation (same as what ResNet was trained with)
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

@app.route('/infer', methods=['POST'])
def infer():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    image = Image.open(io.BytesIO(file.read()))
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    img_tensor = preprocess(image).unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        output = model(img_tensor)
        _, predicted = torch.max(output, 1)

    return jsonify({"predicted_class": predicted.item()}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
