console.log('clearHistory.js loaded'); // Debug loading

function clearHistory() {
    console.log('clearHistory function called'); // Debug function call
    
    if (confirm('Are you sure you want to clear your entire history?')) {
        console.log('User confirmed clear history'); // Debug confirmation
        
        fetch('/clear_history', {
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
                // Reload the page to show empty history
                window.location.reload();
            } else {
                alert('Failed to clear history: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to clear history. Please try again.');
        });
    }
} 