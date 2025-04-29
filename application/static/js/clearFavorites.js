console.log('clearFavorites.js loaded'); // Debug loading

function clearFavorites() {
    console.log('clearFavorites function called'); // Debug function call
    
    if (confirm('Are you sure you want to clear all your favorites?')) {
        console.log('User confirmed clear favorites'); // Debug confirmation
        
        fetch('/clear_favorites', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            console.log('Response received:', response); // Debug response
            return response.json();
        })
        .then(data => {
            console.log('Data received:', data); // Debug data
            if (data.status === 'success') {
                window.location.reload();
            } else {
                alert('Failed to clear favorites: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to clear favorites. Please try again.');
        });
    }
} 