let currentAssessment = null;
let currentQuestions = [];
let currentResponses = [];
let currentQuestionIndex = 0;

document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) return;
});

function selectAssessmentType(type) {
    // Update active button
    document.querySelectorAll('.type-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    currentAssessment = type;
}

async function startAssessment() {
    if (!currentAssessment) {
        alert('Please select an assessment type');
        return;
    }

    try {
        const response = await fetch(`http://localhost:5000/api/assessment/questions?type=${currentAssessment}`, {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        
        if (data.success) {
            currentQuestions = data.questions;
            currentResponses = new Array(currentQuestions.length).fill(null);
            currentQuestionIndex = 0;
            
            // Show assessment interface
            document.getElementById('typeSelection').classList.add('hidden');
            document.getElementById('assessmentQuestions').classList.remove('hidden');
            
            // Set assessment info
            document.getElementById('assessmentTitle').textContent = data.title;
            document.getElementById('assessmentInstructions').textContent = data.instructions;
            
            loadQuestion();
        } else {
            alert('Error loading assessment: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error. Please try again.');
    }
}

function loadQuestion() {
    const questionsContainer = document.getElementById('questionsContainer');
    const progressFill = document.getElementById('progressFill');
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');
    const submitBtn = document.getElementById('submitBtn');
    
    // Update progress
    const progress = ((currentQuestionIndex + 1) / currentQuestions.length) * 100;
    progressFill.style.width = `${progress}%`;
    
    // Update navigation buttons
    prevBtn.style.display = currentQuestionIndex > 0 ? 'block' : 'none';
    nextBtn.style.display = currentQuestionIndex < currentQuestions.length - 1 ? 'block' : 'none';
    submitBtn.style.display = currentQuestionIndex === currentQuestions.length - 1 ? 'block' : 'none';
    
    // Create question HTML
    questionsContainer.innerHTML = `
        <div class="question-card">
            <div class="question-text">
                ${currentQuestionIndex + 1}. ${currentQuestions[currentQuestionIndex]}
            </div>
            <div class="scale-options">
                <div class="scale-option" data-value="0" onclick="selectResponse(0)">Not at all</div>
                <div class="scale-option" data-value="1" onclick="selectResponse(1)">Several days</div>
                <div class="scale-option" data-value="2" onclick="selectResponse(2)">More than half the days</div>
                <div class="scale-option" data-value="3" onclick="selectResponse(3)">Nearly every day</div>
            </div>
        </div>
    `;
    
    // Highlight selected response if exists
    if (currentResponses[currentQuestionIndex] !== null) {
        const selectedOption = questionsContainer.querySelector(`[data-value="${currentResponses[currentQuestionIndex]}"]`);
        if (selectedOption) {
            selectedOption.classList.add('selected');
        }
    }
}

function selectResponse(value) {
    // Remove selection from all options in current question
    const currentOptions = document.querySelectorAll('.scale-option');
    currentOptions.forEach(option => {
        option.classList.remove('selected');
    });
    
    // Add selection to clicked option
    event.target.classList.add('selected');
    
    // Store response
    currentResponses[currentQuestionIndex] = value;
}

function nextQuestion() {
    if (currentResponses[currentQuestionIndex] === null) {
        alert('Please select a response before continuing');
        return;
    }
    
    currentQuestionIndex++;
    loadQuestion();
}

function previousQuestion() {
    currentQuestionIndex--;
    loadQuestion();
}

async function submitAssessment() {
    if (currentResponses.includes(null)) {
        alert('Please answer all questions before submitting');
        return;
    }

    const totalScore = currentResponses.reduce((sum, response) => sum + response, 0);
    
    try {
        const response = await fetch('http://localhost:5000/api/assessment/submit', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                assessment_type: currentAssessment,
                responses: currentResponses,
                total_score: totalScore
            })
        });

        const data = await response.json();
        
        if (data.success) {
            // Show results
            document.getElementById('assessmentQuestions').classList.add('hidden');
            document.getElementById('assessmentResults').classList.remove('hidden');
            
            document.getElementById('resultScore').textContent = data.result.total_score;
            document.getElementById('resultSeverity').textContent = data.result.severity;
            document.getElementById('resultRecommendation').textContent = data.result.recommendation;
        } else {
            alert('Error submitting assessment: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error. Please try again.');
    }
}

function goToDashboard() {
    window.location.href = 'dashboard.html';
}

function takeAnother() {
    document.getElementById('assessmentResults').classList.add('hidden');
    document.getElementById('typeSelection').classList.remove('hidden');
    currentAssessment = null;
}