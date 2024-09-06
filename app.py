import os
import json
import google.generativeai as genai
from gradio_client import Client

from PIL import Image
from flask import Flask,render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Add CORS support
CORS(app)

@app.route('/', methods=['GET'])
def welcome():
    return render_template('home.html')
 
@app.route('/generate-image', methods=['GET'])
def generate_image():
    # Configuration for Google Generative AI
    api_key = "AIzaSyC6Rzd5oRIfCeqaedazxRCV2Pf3ElNjNqw"
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    chat_session = model.start_chat()

    # Prompt generation
    prompt = """
    Create a random prompt and negative prompt for generating unique scenes. The prompt should be diverse, which can include themes like anime, digital art, studio ghibli art, miyazaki, cyberpunk, steampunk, fantasy landscape, Makoto Shinkai, landscape wallpapers in anime style, lonely path. Include sharp edges and fantasy similar keywords if required. add 8k in the end.The negative prompts should exclude elements like low-quality, blurry, pixelated, bad anatomy, deformed, unrealistic, modern, realistic, mundane, ordinary, boring, and conventional. Give a single prompt.
    Strictly give the response in a json format for example,
    {
        "prompt": "cyberpunk cityscape at night, neon lights, flying cars, futuristic architecture, androids, holographic projections, dark aesthetic",
        "negative-prompt": "low-quality, blurry, pixelated, bad anatomy, deformed, unrealistic"
    }
    or
    {
        "prompt": "anime, space warrior, beautiful, female, ultrarealistic, soft lighting, 8k",
        "negative-prompt": "3d, (deformed eyes, nose, ears, nose), bad anatomy, ugly"
    }
    """

    response = chat_session.send_message(prompt).text

    # Remove extra characters and "json" keyword if present
    clean_response = response.strip().strip('```').replace('json', '').strip()

    # Debugging: print raw response
    print("Clean response:", clean_response)

    # Load the JSON response into a Python dictionary
    try:
        response_dict = json.loads(clean_response)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")
        response_dict = {}

    # Debugging: print parsed response
    print("Parsed response:", response_dict)


    # Get the prompt and negative prompt from the response
    image_prompt = response_dict.get("prompt")
    negative_prompt = response_dict.get("negative-prompt")

    if not image_prompt or not negative_prompt:
        print("Error: 'prompt' or 'negative-prompt' not found in response.")
    else:
        # Configuration for Gradio Client
        client = Client("prodia/sdxl-stable-diffusion-xl")

        # Ensure the downloads folder exists
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        # Generate the image
        result = client.predict(
            prompt=image_prompt,
            negative_prompt=negative_prompt,
            model="realismEngineSDXL_v10.safetensors [af771c3f]",
            steps=20,
            sampler="DPM++ 2M Karras",
            cfg_scale=7,
            resolution="1024x1024",
            seed=757,
            api_name="/flip_text"
        )

        # Debugging: print result from the image generation
        print("Image generation result:", result)

        # Result is expected to be a URL or path to a .webp image
        webp_image_path = result  # Assuming result is the path to the .webp image

        # Function to generate a unique filename
        def get_unique_filename(folder, base_filename, extension):
            i = 1
            while os.path.exists(os.path.join(folder, f"{base_filename}_{i}.{extension}")):
                i += 1
            return os.path.join(folder, f"{base_filename}_{i}.{extension}")

        # Generate unique filename for the new image
        jpg_image_path = get_unique_filename('public/images', 'image', 'jpg')

        # Download the .webp image if result is a URL
        # (Assuming result is a URL, you may need to download it first)
        try:
            from urllib.request import urlretrieve
            urlretrieve(webp_image_path, 'temp_image.webp')
            webp_image_path = 'temp_image.webp'
        except Exception as e:
            print(f"Failed to download image from URL: {e}")
        
        # Open the image and convert it to .jpg
        with Image.open(webp_image_path) as img:
            img.convert('RGB').save(jpg_image_path, 'JPEG')

        print(f"Image saved at: {jpg_image_path}")

        # Clean up temporary file if necessary
        if os.path.exists('temp_image.webp'):
            os.remove('temp_image.webp')
        
    if os.path.exists(jpg_image_path):
        # Ensure the correct image path is returned
        return jsonify({"imageUrl": f"images/{os.path.basename(jpg_image_path)}"})
    else:
        return jsonify({"error": "Image generation failed."}), 500


if __name__ == '__main__':
    # Ensure the static/images folder exists
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)