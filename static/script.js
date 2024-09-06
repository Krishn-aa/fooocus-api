document.getElementById('generate-button').addEventListener('click', async () => {
    const messageDiv = document.getElementById('message');
    const imageList = document.getElementById('image-list');

    messageDiv.textContent = 'Generating...';

    try {
        const response = await fetch('http://127.0.0.1:5000/generate-image');
        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }
        const result = await response.json();

        if (result.imageUrl) {
            const img = document.createElement('img');
            img.src = result.imageUrl;

            const imageContainer = document.createElement('div');
            imageContainer.classList.add('image-container');
            imageContainer.appendChild(img);

            imageList.appendChild(imageContainer);
            messageDiv.textContent = 'Image generated successfully!';
        } else {
            throw new Error('No image URL found in response.');
        }
    } catch (error) {
        console.error('Error:', error);
        messageDiv.textContent = 'Failed to generate image.';
    }
});
