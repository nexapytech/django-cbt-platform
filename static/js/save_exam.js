export function autoSaveExam() {
  
    // Prepare the data object to send
    var formData = {
        'uuid': document.getElementById("exam-uuid").value,
        'exam_title': document.getElementById('exam-title').value,
        'exam_description': document.getElementById('exam-description').value,
        'questions': []
    };

    // Get all question items
    var questions = document.querySelectorAll('.question-item');
    

    questions.forEach(function (question, index) {
        var questionData = {
            'id': index + 1, // Assign a numerical ID based on the question index (1-based index)
            'title': question.querySelector('.question-title').value,
            'type': question.querySelector('.question-type').value, // Short answer, paragraph, multiple choice
            'options': [], // Options will only be collected if it's a multiple-choice question
            'answers': null
        };
        
    
        if (questionData.type === 'short-answer') {
            // For short-answer and paragraph, just fetch the answer field value
            questionData.answers = question.querySelector('.short-text-answer').value;
        }
        if (questionData.type === 'paragraph') {
            // For short-answer and paragraph, just fetch the answer field value
            questionData.answers = question.querySelector('.paragraph-text-answer').value;
        }
        // If it's a multiple choice question, collect the options
        if (questionData.type === "multiple-choice") {
            var options = question.querySelectorAll('.option-text');
            options.forEach(function(option) {
                questionData.options.push(option.value);
            });
            questionData.answers = question.querySelector('.multichoice-answer').value;
        }
        

        // If it's short-answer or paragraph, no options need to be added, just push the question
        formData.questions.push(questionData);
     
         document.querySelector('.data-save').innerHTML="saving..."
    });



    // Send the collected data as a JSON object
    fetch('/save_exam', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            
        },
        body: JSON.stringify(formData)  // Send the data as JSON
    
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            document.querySelector('.data-save').innerHTML="saved";
        } else {
            document.querySelector('.data-save').innerHTML="error";
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('There was an error submitting the form.');
    });
}

// Attach auto-save to input and change events for relevant elements
document.querySelectorAll("input, textarea, select").forEach((element) => {
    element.addEventListener("input", autoSaveExam);
});

// Attach auto-save to change events for buttons if they affect the data
document.querySelectorAll("button:not(.exclude-save)").forEach((button) => {
    button.addEventListener("click", autoSaveExam);

// Specifically target option-text elements
document.querySelectorAll(".option-text").forEach((element) => {
    element.addEventListener("input", autoSaveExam);
});    
});


