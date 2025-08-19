document.getElementById('repo-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const owner = document.getElementById('owner').value;
    const repo = document.getElementById('repo').value;
    const statusDiv = document.getElementById('status');
    const downloadLinksDiv = document.getElementById('download-links');

    // Reset previous results
    statusDiv.innerHTML = '';
    downloadLinksDiv.innerHTML = '';

    // Show loading
    statusDiv.innerHTML = 'Processing... This may take a few minutes.';

    try {
        const response = await fetch('/run_github_gather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ owner, repo })
        });

        const result = await response.json();

        if (result.success) {
            statusDiv.innerHTML = 'Commit data gathered successfully!';
            
            // Create file name display
            const package = `${owner}-${repo}`;
            const links = [
                { name: 'Commits with Description', file: `data/${package}-commits_w_desc.csv` },
                { name: 'Commits', file: `data/${package}-commits.csv` },
                { name: 'Monthly Commits', file: `data/${package}-monthly.csv` }
            ];

            downloadLinksDiv.innerHTML = links.map(link => 
                `${link.name}: ${link.file}`
            ).join('<br>');
        } else {
            statusDiv.innerHTML = `Error: ${result.error}`;
        }
    } catch (error) {
        statusDiv.innerHTML = `Error: ${error.message}`;
    }
});

// Bass Model Fitting Button Event Listener
document.getElementById('fit-bass-model').addEventListener('click', async () => {
    const owner = document.getElementById('owner').value;
    const repo = document.getElementById('repo').value;
    const bassModelStatusDiv = document.getElementById('bass-model-status');
    const bassModelImagesDiv = document.getElementById('bass-model-images');

    // Reset previous results
    bassModelStatusDiv.innerHTML = '';
    bassModelImagesDiv.innerHTML = '';

    // Validate input
    if (!owner || !repo) {
        bassModelStatusDiv.innerHTML = 'Please enter repository owner and name first.';
        return;
    }

    // Show loading
    bassModelStatusDiv.innerHTML = 'Fitting Bass Model... This may take a few minutes.';

    try {
        const response = await fetch('/run_bass_model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ owner, repo })
        });

        const result = await response.json();

        if (result.success) {
            bassModelStatusDiv.innerHTML = 'Bass Model Fitting Completed!';
            
            // Display output text
            bassModelStatusDiv.innerHTML += `<pre>${result.output}</pre>`;

            // Display generated images
            if (result.images && result.images.length > 0) {
                const imagesHTML = result.images.map(imagePath => {
                    return `<div class="image-container">Image: ${imagePath}</div>`;
                }).join('');
                bassModelImagesDiv.innerHTML = `<h4>Bass Model Visualizations</h3>${imagesHTML}`;
            }
        } else {
            bassModelStatusDiv.innerHTML = `Error: ${result.error}`;
        }
    } catch (error) {
        bassModelStatusDiv.innerHTML = `Error: ${error.message}`;
    }
});

// Innovation Model Fitting Button Event Listener
document.getElementById('fit-innovation-model').addEventListener('click', async () => {
    const owner = document.getElementById('owner').value;
    const repo = document.getElementById('repo').value;
    const innovationModelStatusDiv = document.getElementById('innovation-model-status');
    const innovationModelImagesDiv = document.getElementById('innovation-model-images');

    // Reset previous results
    innovationModelStatusDiv.innerHTML = '';
    innovationModelImagesDiv.innerHTML = '';

    // Validate input
    if (!owner || !repo) {
        innovationModelStatusDiv.innerHTML = 'Please enter repository owner and name first.';
        return;
    }

    // Show loading
    innovationModelStatusDiv.innerHTML = 'Fitting Growth Model... This may take a few minutes.';

    try {
        const response = await fetch('/run_innovation_model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ owner, repo })
        });

        const result = await response.json();

        if (result.success) {
            innovationModelStatusDiv.innerHTML = 'Growth Model Fitting Completed!';
            
            // Display output text
            innovationModelStatusDiv.innerHTML += `<pre>${result.output}</pre>`;

            // Display generated images
            if (result.images && result.images.length > 0) {
                const imagesHTML = result.images.map(imagePath => {
                    return `<div class="image-container">Image: ${imagePath}</div>`;
                }).join('');
                innovationModelImagesDiv.innerHTML = `<h4>Growth Visualizations</h3>${imagesHTML}`;
            }
        } else {
            innovationModelStatusDiv.innerHTML = `Error: ${result.error}`;
        }
    } catch (error) {
        innovationModelStatusDiv.innerHTML = `Error: ${error.message}`;
    }
});
