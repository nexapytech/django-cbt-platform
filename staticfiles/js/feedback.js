document.querySelector('#feedbackForm').addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent default form submission behavior
   

    try {
        const feedbackTextarea = document.querySelector('#feedback'); // Textarea input
        const feedback = feedbackTextarea.value.trim(); // Get and trim feedback text
        exam_id = document.querySelector('#exam-id')
        // Send feedback to the server
        const response = await fetch('/feedback_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value // CSRF Token for Django
            },
            body: JSON.stringify({
                feedback: feedback // Send feedback text
            })
        });

        const data = await response.json(); // Parse server response

        if (data.success) {
            // Feedback submitted successfully
            
           swal('Candidate Feedback', data.success, 'success')
            feedbackTextarea.value = ''; // Clear the textarea
        } else {
            // Error from the server
            swal('Candidate Feedback', "An error occurred", 'error')
        }
    } catch (error) {
        // Handle fetch or network errors
        alert("Something went wrong. Please try again later.");
      
    }
});
