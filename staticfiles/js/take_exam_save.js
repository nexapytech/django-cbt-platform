export function autoSaveExam() {
  
  // Prepare the data object to send
var formData = {
    'uuid': document.getElementById("exam-uuid").value,
    'publish_hash': document.getElementById("published_hash").value,
    'questions': [] 
};

// Get all question items
var questions = document.querySelectorAll('.question-item');
questions.forEach(function(question) {
    var questionData = {
        'id': question.getAttribute('data-id'), // Fetch the ID from the data-id attribute
        'title': question.querySelector('.question-text').textContent,
        'type': null, // Initially set type as null
        'answers': null
    };


    // Determine the question type and fetch the appropriate answers
    if (question.querySelector('.form-check-input')) {
        // Multiple Choice question
        questionData.type = 'multiple-choice';
        const selectedOption = question.querySelector('.form-check-input:checked');
        if (selectedOption) {
            questionData.answers = selectedOption.value;
        } else {
            questionData.answers = null;
        }
    }

    if (question.querySelector('.form-text-input')) {
        // Short Answer question
        questionData.type = 'short-answer';
        questionData.answers = question.querySelector('.form-text-input').value;
    }

    if (question.querySelector('.paragraphInput')) {
        // Paragraph Answer question (textarea)
        questionData.type = 'paragraph';
        questionData.answers = question.querySelector('.paragraphInput').value;
    }

    // Push the data to the formData.questions array
    formData.questions.push(questionData);

 
});

// Optionally, save the data
//document.querySelector('.data-save').innerHTML = "Saving...";

    // Send the collected data as a JSON object
    fetch('/save_exam_answer', {
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

//---------------------------------------browser lock -------------------------------------------------------------
 // Prevent right-click
    document.addEventListener('contextmenu', (event) => {
        event.preventDefault();
        
    });



    // Prevent page reload
window.onbeforeunload = function() {
    
};
window.onfocus = function() {
    const endExamButton = document.querySelector('.endexam-btn');
    endExamButton.click();
};
window.addEventListener("blur", function() {
    const endExamButton = document.querySelector('.endexam-btn');
    endExamButton.click();
});

document.addEventListener('keydown', function(event) {
    if (event.ctrlKey) {
        event.preventDefault();
       
    }
    if (event.key === 'Meta' || event.key === 'OS') {
        event.preventDefault();
        const endExamButton = document.querySelector('.endexam-btn');
        endExamButton.click();
       
    }
    if (event.key === 'F12') {
        event.preventDefault();
        const endExamButton = document.querySelector('.endexam-btn');
        endExamButton.click();
      
    }

    // Prevent Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U, or Ctrl+Shift+C
    if (
        (event.ctrlKey && event.shiftKey && ['I', 'J', 'C'].includes(event.key)) ||
        (event.ctrlKey && event.key === 'U')
    ) {
        event.preventDefault();
        const endExamButton = document.querySelector('.endexam-btn');
        endExamButton.click();
       
    }
});



//------------------------exam timmer-------------------------------------------------
const timerElement = document.getElementById('exam-timer');
const alertElement = document.getElementById('alert');

// Backend-provided duration in minutes
let duration = examDuration  // Convert minutes to seconds

function showAlert(message) {
    alertElement.textContent = message;
    alertElement.style.display = 'block';

    setTimeout(() => {
        alertElement.style.display = 'none';
    }, 5000); // Hide alert after 5 seconds
}

function startCountdown() {
    const interval = setInterval(() => {
        const hours = Math.floor(duration / 3600);
        const minutes = Math.floor((duration % 3600) / 60);
        const seconds = duration % 60;

        // Display the time in HH:MM:SS format
        timerElement.textContent = `Time Left: ${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

        // Trigger alerts at 5 minutes and 1 minute remaining
        if (duration === 300 || duration === 60) {
            const timeLeft = duration === 300 ? "5 minutes" : "1 minute";
            timerElement.style.color='red'; // Make the timer red
            showAlert(`Hurry up! You have ${timeLeft} left.`);
        }

       
        duration--;

        // When time runs out
        if (duration < 0) {
            clearInterval(interval);
            timerElement.textContent = "Time's Up!";
             // Submit the form automatically
             const endExamButton = document.querySelector('.endexam-btn');
             endExamButton.click();
        }
    }, 1000);
  
}

startCountdown();


//-------------------------------------------------end exam-------------------------------------endExam
function handleEndExamSubmission() {

$(document).on('submit', '#endForm', function(e){
    const icon = document.querySelector('.examendicon')
    const endexam  = document.querySelector('#endexam-btn-text')
    icon.style.display='inline-block'
    endexam.textContent="loading.."
   

    e.preventDefault();
   

    var formData = new FormData(this);
    $.ajax({
        type:'POST',
        url:'/end_exam',
        processData: false,
        contentType: false,
        data: formData,

        success: function(data){
            if ('success' in data) {
                setTimeout(()=>{
 
                    icon.style.display='none'  
                    endexam.textContent="End Exam"  
                    window.location.reload()        
                }, 500)}

                if ('redirect' in data) {
                    setTimeout(()=>{
     
                        icon.style.display='none'  
                        endexam.textContent="End Exam"  
                         // Redirect to /feedback (appended to the current domain)
                         window.location.href = window.location.origin + '/feedback';
                    }, 500)}
                   
               
                 
                
            
               
           
             
            
              
            },
           
           
           
           error:function(data){
            setTimeout(()=>{
                endexam.textContent="End Exam"  
               
           icon.style.display = 'none'
         
             alert(data.error)
           
            }, 500)

        }

    })
               
})


}




handleEndExamSubmission()