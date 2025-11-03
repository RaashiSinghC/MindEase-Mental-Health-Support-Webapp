const API_BASE = window.API_BASE || 'https://mindease-backend-s59o.onrender.com/api';
let selectedMood = null;

// Initialize mood selection
document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) return;
    
    console.log('Mood tracker initialized');
    initializeMoodSelection();
    loadMoodInsights();
});

function initializeMoodSelection() {
    const moodOptions = document.querySelectorAll('.mood-option');
    console.log('Found mood options:', moodOptions.length);
    
    moodOptions.forEach(option => {
        option.addEventListener('click', function() {
            const moodValue = this.getAttribute('data-value');
            console.log('Mood option clicked:', moodValue);
            
            // Remove selected class from all options
            moodOptions.forEach(o => {
                o.classList.remove('selected');
                o.style.transform = 'scale(1)';
            });
            
            // Add selected class to clicked option
            this.classList.add('selected');
            this.style.transform = 'scale(1.05)';
            
            // Store selected mood value
            selectedMood = moodValue;
            console.log('Selected mood stored:', selectedMood);
        });
    });
}

async function saveMood() {
    console.log('Save mood function called');
    
    if (!selectedMood) {
        alert('Please select a mood first!');
        return;
    }

    const notes = document.getElementById('mood-notes').value;
    console.log('Mood data:', { mood_score: selectedMood, notes: notes });

    const moodData = {
        mood_score: parseInt(selectedMood),
        notes: notes
    };

    try {
        console.log('Sending mood data to server...');
        const response = await fetch(`${API_BASE}/mood/entry`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(moodData)
        });

        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Mood save response:', data);
        
        if (response.ok) {
            alert('Mood saved successfully! 😊');
            resetMoodForm();
            loadMoodInsights();
        } else {
            alert('Failed to save mood: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error saving mood:', error);
        alert('Network error. Please check if the server is running and try again.');
    }
}

function resetMoodForm() {
    console.log('Resetting mood form');
    // Remove selection from all mood options
    const moodOptions = document.querySelectorAll('.mood-option');
    moodOptions.forEach(option => {
        option.classList.remove('selected');
        option.style.transform = 'scale(1)';
    });
    
    // Clear notes
    document.getElementById('mood-notes').value = '';
    selectedMood = null;
    console.log('Mood form reset complete');
}

async function loadMoodInsights() {
    console.log('Loading mood insights...');
    try {
        const response = await fetch(`http://localhost:5000/api/mood/insights`, {
            headers: getAuthHeaders()
        });
        
        console.log('Insights response status:', response.status);
        const data = await response.json();
        console.log('Insights data:', data);
        
        if (response.ok) {
            displayInsights(data);
        } else {
            console.error('Error loading insights:', data.message);
        }
    } catch (error) {
        console.error('Error loading insights:', error);
    }
}

function displayInsights(insights) {
    const insightsDiv = document.getElementById('mood-insights');
    console.log('Displaying insights:', insights);
    
    if (insights.message && insights.message.includes("Not enough data")) {
        insightsDiv.innerHTML = `
            <p>📊 Start tracking your mood daily to unlock personalized insights!</p>
            <p>We'll help you identify patterns and provide recommendations.</p>
        `;
        return;
    }
    
    insightsDiv.innerHTML = `
        <p><strong>Average Mood:</strong> ${insights.average_mood}/5</p>
        <p><strong>Insight:</strong> ${insights.insight}</p>
        <p><strong>Recommendation:</strong> ${insights.recommendation}</p>
        <p><em>Based on ${insights.total_entries} mood entries</em></p>
    `;
}

function goToDashboard() {
    window.location.href = 'dashboard.html';
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    window.location.href = 'index.html';
}

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return true;

}
