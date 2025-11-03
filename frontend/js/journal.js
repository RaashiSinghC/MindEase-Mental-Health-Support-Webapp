document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) return;
    
    // Load journal entries and analytics
    loadJournalEntries();
    loadJournalAnalytics();
    
    // Set up form submission
    const journalForm = document.getElementById('journalForm');
    if (journalForm) {
        journalForm.addEventListener('submit', function(event) {
            event.preventDefault();
            saveJournalEntry();
        });
    }
});

async function saveJournalEntry() {
    const title = document.getElementById('entryTitle').value;
    const content = document.getElementById('entryContent').value;
    
    if (!content.trim()) {
        alert('Please write something in your journal entry');
        return;
    }
    
    try {
        const response = await fetch('http://localhost:5000/api/journal/entry', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                title: title || 'Journal Entry',
                content: content
            })
        });

        const data = await response.json();
        
        if (data.success) {
            alert('Journal entry saved! 📝');
            
            // Clear form
            document.getElementById('journalForm').reset();
            
            // Reload entries and analytics
            loadJournalEntries();
            loadJournalAnalytics();
        } else {
            alert('Error saving entry: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error. Please try again.');
    }
}

async function loadJournalEntries() {
    try {
        const response = await fetch(`http://localhost:5000/api/journal/entries`, {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        
        const entriesList = document.getElementById('entriesList');
        
        if (data.success && data.entries && data.entries.length > 0) {
            entriesList.innerHTML = '';
            
            data.entries.slice(0, 5).forEach((entry) => {
                const entryDate = new Date(entry.timestamp).toLocaleDateString();
                const sentimentClass = `sentiment-${entry.sentiment}`;
                const sentimentText = entry.sentiment ? entry.sentiment.charAt(0).toUpperCase() + entry.sentiment.slice(1) : 'Neutral';
                
                const emotionsHTML = entry.emotions && entry.emotions.length > 0 
                    ? entry.emotions.map(emotion => `<span class="emotion-tag">${emotion}</span>`).join('')
                    : '';
                
                const entryHTML = `
                    <div class="journal-entry">
                        <div class="entry-header">
                            <h4 class="entry-title">${entry.title || 'Journal Entry'}</h4>
                            <span class="entry-date">${entryDate}</span>
                        </div>
                        <div class="entry-content">${entry.content}</div>
                        <div class="entry-analysis">
                            <span class="sentiment-indicator ${sentimentClass}">${sentimentText}</span>
                            ${emotionsHTML}
                            <span style="margin-left: auto; color: #666;">${entry.word_count || 0} words</span>
                        </div>
                    </div>
                `;
                
                entriesList.innerHTML += entryHTML;
            });
        } else {
            entriesList.innerHTML = '<p>No journal entries yet. Start writing!</p>';
        }
    } catch (error) {
        console.error('Error loading entries:', error);
        entriesList.innerHTML = '<p>Error loading entries. Please try again.</p>';
    }
}

async function loadJournalAnalytics() {
    try {
        const response = await fetch(`http://localhost:5000/api/journal/analytics`, {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        
        if (data.success && data.analytics) {
            const analytics = data.analytics;
            
            // Update word count
            const totalWords = analytics.writing_insights?.total_words_written || 0;
            const totalWordsElement = document.getElementById('totalWords');
            if (totalWordsElement) {
                totalWordsElement.textContent = totalWords.toLocaleString();
            }
            
            // Update sentiment chart
            const sentimentDiv = document.getElementById('sentimentChart');
            if (sentimentDiv && analytics.sentiment_distribution) {
                let sentimentHTML = '';
                for (const [sentiment, count] of Object.entries(analytics.sentiment_distribution)) {
                    const percentage = (count / analytics.total_entries * 100).toFixed(1);
                    sentimentHTML += `
                        <div style="margin: 0.5rem 0;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>${sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}</span>
                                <span>${percentage}%</span>
                            </div>
                            <div style="background: #e9ecef; height: 8px; border-radius: 4px; margin-top: 0.2rem;">
                                <div style="background: var(--primary); height: 100%; width: ${percentage}%; border-radius: 4px;"></div>
                            </div>
                        </div>
                    `;
                }
                sentimentDiv.innerHTML = sentimentHTML;
            }
            
            // Update emotions list
            const emotionsDiv = document.getElementById('emotionsList');
            if (emotionsDiv && analytics.common_emotions && Object.keys(analytics.common_emotions).length > 0) {
                emotionsDiv.innerHTML = Object.entries(analytics.common_emotions)
                    .map(([emotion, count]) => 
                        `<span class="emotion-tag">${emotion} (${count})</span>`
                    ).join('');
            } else if (emotionsDiv) {
                emotionsDiv.innerHTML = '<p>Write more to detect emotional themes</p>';
            }
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}