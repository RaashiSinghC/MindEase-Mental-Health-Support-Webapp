const API_BASE = window.API_BASE || 'https://mindease-backend-s59o.onrender.com/api';
// Analytics Report JavaScript
document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) return;
    loadAnalyticsReport();
});


async function loadAnalyticsReport() {
    try {
        const response = await fetch(`${API_BASE}/analytics/comprehensive-report`, {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayAnalyticsReport(data.report);
        } else {
            console.error('Error loading analytics:', data.error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function displayAnalyticsReport(report) {
    // Update report period
    document.getElementById('reportPeriod').textContent = 
        `${report.time_period.start_date} to ${report.time_period.end_date}`;
    
    // Display engagement metrics
    displayEngagementMetrics(report.engagement_metrics);
    
    // Display mood analysis
    displayMoodAnalysis(report.mood_analysis);
    
    // Display journal insights
    displayJournalInsights(report.journal_insights);
    
    // Display assessment history
    displayAssessmentHistory(report.assessment_history);
    
    // Display weekly comparison
    displayWeeklyComparison(report.weekly_comparison);
    
    // Display recommendations
    displayRecommendations(report.recommendations);
}

function displayEngagementMetrics(metrics) {
    const container = document.getElementById('engagementMetrics');
    
    if (metrics.message) {
        container.innerHTML = `<p>${metrics.message}</p>`;
        return;
    }
    
    container.innerHTML = `
        <div class="metric-item">
            <div class="metric-label">Mood Entries</div>
            <div class="metric-value">${metrics.mood_entries}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Journal Entries</div>
            <div class="metric-value">${metrics.journal_entries}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Consistency Score</div>
            <div class="metric-value">${metrics.consistency_score}%</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Active Days</div>
            <div class="metric-value">${metrics.active_days} out of ${metrics.total_days}</div>
        </div>
    `;
}

function displayMoodAnalysis(analysis) {
    const container = document.getElementById('moodAnalysis');
    
    if (analysis.message) {
        container.innerHTML = `<p>${analysis.message}</p>`;
        return;
    }
    
    const trendClass = analysis.mood_trend === 'improving' ? 'trend-up' : 
                      analysis.mood_trend === 'declining' ? 'trend-down' : 'trend-stable';
    
    container.innerHTML = `
        <div class="metric-item">
            <div class="metric-label">Average Mood</div>
            <div class="metric-value">${analysis.average_mood}/5</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Trend</div>
            <div class="metric-value ${trendClass}">${analysis.mood_trend}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Mood Stability</div>
            <div class="metric-value">${analysis.mood_stability}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Best Mood Day</div>
            <div class="metric-value">${analysis.best_mood_day}</div>
        </div>
    `;
}

function displayJournalInsights(insights) {
    const container = document.getElementById('journalInsights');
    
    if (insights.message) {
        container.innerHTML = `<p>${insights.message}</p>`;
        return;
    }
    
    container.innerHTML = `
        <div class="metric-item">
            <div class="metric-label">Total Entries</div>
            <div class="metric-value">${insights.total_entries}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Total Words</div>
            <div class="metric-value">${insights.total_words}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Average Length</div>
            <div class="metric-value">${insights.avg_entry_length} words</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Writing Frequency</div>
            <div class="metric-value">${insights.writing_frequency}</div>
        </div>
    `;
}

function displayAssessmentHistory(history) {
    const container = document.getElementById('assessmentHistory');
    
    if (!history || history.length === 0) {
        container.innerHTML = '<p>No assessment history available</p>';
        return;
    }
    
    let html = '';
    history.forEach(assessment => {
        html += `
            <div class="metric-item">
                <div class="metric-label">${assessment.type} - ${assessment.date}</div>
                <div class="metric-value">Score: ${assessment.score} (${assessment.severity})</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function displayWeeklyComparison(comparison) {
    const container = document.getElementById('weeklyComparison');
    
    const trendClass = comparison.trend === 'improving' ? 'trend-up' : 
                      comparison.trend === 'declining' ? 'trend-down' : 'trend-stable';
    
    container.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; text-align: center;">
            <div>
                <div style="font-size: 0.9rem; color: #666;">Current Week</div>
                <div style="font-size: 2rem; font-weight: bold;">${comparison.current_week_avg}</div>
            </div>
            <div>
                <div style="font-size: 0.9rem; color: #666;">Previous Week</div>
                <div style="font-size: 2rem; font-weight: bold;">${comparison.previous_week_avg}</div>
            </div>
        </div>
        <div style="text-align: center; margin-top: 1rem;">
            <div class="${trendClass}">Trend: ${comparison.trend} (${comparison.change >= 0 ? '+' : ''}${comparison.change})</div>
        </div>
    `;
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsList');
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<p>No specific recommendations at this time.</p>';
        return;
    }
    
    let html = '';
    recommendations.forEach(rec => {
        html += `<div class="recommendation-item">${rec}</div>`;
    });
    
    container.innerHTML = html;
}

function generatePDFReport() {
    alert('PDF generation would be implemented here! For now, you can print this page.');
    window.print();

}

