const API_BASE = window.API_BASE || 'https://mindease-backend-s59o.onrender.com/api';
// Game Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) return;
    loadGameProgress();
});

async function loadGameProgress() {
    try {
        const response = await fetch(`${API_BASE}/game/progress`, {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        console.log('Game progress response:', data);
        
        if (data.success) {
            displayGameProgress(data.progress, data.activity_counts);
        } else {
            console.error('Error loading game progress:', data.error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function displayGameProgress(progress, activityCounts) {
    // Update level and points
    document.getElementById('levelBadge').textContent = progress.level;
    document.getElementById('userPoints').textContent = `${progress.points} points`;
    document.getElementById('levelProgress').style.width = `${progress.progress_percentage}%`;
    document.getElementById('streakDisplay').textContent = `${progress.streak_days} days`;
    
    // Update activity counts
    document.getElementById('moodCount').textContent = activityCounts.mood_entries;
    document.getElementById('journalCount').textContent = activityCounts.journal_entries;
    document.getElementById('assessmentCount').textContent = activityCounts.assessments;
    document.getElementById('chatCount').textContent = activityCounts.chat_sessions;
    
    // Next level info
    if (progress.next_level) {
        document.getElementById('nextLevelInfo').innerHTML = 
            `Next: <strong>${progress.next_level.title}</strong> (${progress.next_level.points_needed} points needed)`;
    } else {
        document.getElementById('nextLevelInfo').innerHTML = 
            `🎉 You've reached the highest level!`;
    }
    
    // Display achievements
    displayAchievements(progress.achievements);
    
    // Update dashboard preview
    updateDashboardPreview(progress, activityCounts);
}

function displayAchievements(achievements) {
    const achievementsGrid = document.getElementById('achievementsGrid');
    
    // Define all possible achievements
    const ACHIEVEMENTS_CONFIG = {
        'first_mood': {name: 'First Step', description: 'Track your first mood', points: 20},
        'week_streak': {name: 'Weekly Warrior', description: '7-day activity streak', points: 50},
        'journal_enthusiast': {name: 'Journal Enthusiast', description: 'Write 5 journal entries', points: 30},
        'mood_analyst': {name: 'Mood Analyst', description: 'Track mood for 7 days', points: 40},
        'assessment_pro': {name: 'Assessment Pro', description: 'Complete both assessments', points: 25},
        'chat_regular': {name: 'Chat Regular', description: 'Have 5 chat conversations', points: 20},
        'self_care_champ': {name: 'Self-Care Champion', description: 'Complete 10 exercises', points: 60}
    };
    
    if (!achievements || achievements.length === 0) {
        achievementsGrid.innerHTML = '<p>No achievements yet. Start using MindEase to earn achievements!</p>';
        return;
    }
    
    let html = '';
    
    // Display earned achievements
    achievements.forEach(achievementId => {
        const achievement = ACHIEVEMENTS_CONFIG[achievementId];
        if (achievement) {
            html += `
                <div class="achievement-card">
                    <div class="achievement-name">${achievement.name} ✅</div>
                    <div class="achievement-desc">${achievement.description}</div>
                    <div class="achievement-points">+${achievement.points} points</div>
                </div>
            `;
        }
    });
    
    // Display locked achievements (optional)
    Object.keys(ACHIEVEMENTS_CONFIG).forEach(achievementId => {
        if (!achievements.includes(achievementId)) {
            const achievement = ACHIEVEMENTS_CONFIG[achievementId];
            html += `
                <div class="achievement-card locked">
                    <div class="achievement-name">${achievement.name} 🔒</div>
                    <div class="achievement-desc">${achievement.description}</div>
                    <div class="achievement-points">+${achievement.points} points</div>
                </div>
            `;
        }
    });
    
    achievementsGrid.innerHTML = html;
}

function updateDashboardPreview(progress, activityCounts) {
    if (document.getElementById('previewLevel')) {
        document.getElementById('previewLevel').textContent = progress.level;
        document.getElementById('previewPoints').textContent = progress.points;
        document.getElementById('previewStreak').textContent = `${progress.streak_days} days`;
    }
}

// Add this function to manually update progress (for testing)
async function manualUpdateProgress() {
    try {
        const response = await fetch('http://localhost:5000/api/game/update-progress', {
            method: 'POST',
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Progress updated!');
            loadGameProgress(); // Reload the progress
        }
    } catch (error) {
        console.error('Error updating progress:', error);
    }
}

function viewGameDashboard() {
    window.location.href = 'game-dashboard.html';
}

function viewAnalyticsReport() {
    window.location.href = 'analytics-report.html';

}
