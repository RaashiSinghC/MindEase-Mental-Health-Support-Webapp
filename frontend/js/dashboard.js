// Check if user is logged in
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    window.location.href = 'index.html';
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) return;
    
    loadDashboardData();
    loadRecentMoodEntries();
});

// Load dashboard data
function loadDashboardData() {
    console.log('Loading dashboard data...');
    // Add any additional dashboard data loading here
}

// Load recent mood entries for dashboard
async function loadRecentMoodEntries() {
    try {
        const response = await fetch('http://localhost:5000/api/mood/history', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        console.log('Mood history response:', data);
        
        if (response.ok) {
            displayRecentMoods(data.mood_history);
        } else {
            console.error('Error loading mood history:', data.message);
            document.getElementById('mood-history').innerHTML = '<p>Error loading mood history</p>';
        }
    } catch (error) {
        console.error('Error loading mood entries:', error);
        document.getElementById('mood-history').innerHTML = '<p>Error loading mood entries</p>';
    }
}

// Display recent mood entries on dashboard
function displayRecentMoods(moodEntries) {
    const moodHistoryDiv = document.getElementById('mood-history');
    
    if (!moodEntries || moodEntries.length === 0) {
        moodHistoryDiv.innerHTML = `
            <h2>Recent Mood Entries</h2>
            <p>No mood entries yet. <a href="mood-tracker.html">Start tracking your mood!</a></p>
        `;
        return;
    }
    
    let html = `<h2>Recent Mood Entries</h2><div class="mood-entries-list">`;
    
    moodEntries.slice(0, 5).forEach(entry => {
        const moodEmoji = getMoodEmoji(entry.mood_score);
        const date = new Date(entry.timestamp).toLocaleDateString();
        const time = new Date(entry.timestamp).toLocaleTimeString();
        
        html += `
            <div class="mood-entry-item">
                <div class="mood-emoji">${moodEmoji}</div>
                <div class="mood-details">
                    <div class="mood-score">Mood: ${entry.mood_score}/5</div>
                    <div class="mood-time">${date} at ${time}</div>
                    ${entry.notes ? `<div class="mood-notes">"${entry.notes}"</div>` : ''}
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    moodHistoryDiv.innerHTML = html;
}

// Get emoji for mood score
function getMoodEmoji(score) {
    switch(score) {
        case 1: return '😢';
        case 2: return '😞';
        case 3: return '😐';
        case 4: return '😊';
        case 5: return '😁';
        default: return '😐';
    }
}
// Add these functions to your dashboard.js

function viewGameDashboard() {
    console.log('Navigating to game dashboard...');
    window.location.href = 'game-dashboard.html';
}

function viewAnalyticsReport() {
    console.log('Navigating to analytics report...');
    window.location.href = 'analytics-report.html';
}

// Also update your existing dashboard.js to include game progress loading
document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) return;
    
    loadDashboardData();
    loadRecentMoodEntries();
    loadGamePreview(); // Add this line
});

// Add this function to load game preview on dashboard
async function loadGamePreview() {
    try {
        const response = await fetch('http://localhost:5000/api/game/progress', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateGamePreview(data.progress);
        }
    } catch (error) {
        console.error('Error loading game preview:', error);
    }
}

function updateGamePreview(progress) {
    const previewLevel = document.getElementById('previewLevel');
    const previewPoints = document.getElementById('previewPoints');
    const previewStreak = document.getElementById('previewStreak');
    
    if (previewLevel) previewLevel.textContent = progress.level;
    if (previewPoints) previewPoints.textContent = progress.points;
    if (previewStreak) previewStreak.textContent = `${progress.streak_days} days`;
}