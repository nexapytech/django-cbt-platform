//------------------------------- upload files --------------------------------------------------------
document.querySelector('#uploadFormQuestion').addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent the default form submission

    try {
        // Get the form data
        const form = event.target;
        const formData = new FormData(form);

        // Send the request to the server
        const response = await fetch('/upload_questions', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // Include CSRF token
            },
            body: formData, // Attach form data, including the file
        });

        // Parse the JSON response
        const data = await response.json();

        // Handle success or error responses
        if (data.success) {
            // Show a success alert using SweetAlert or similar
            swal('Question Upload', data.success, 'success') .then(() => {
                // Action to perform after the alert is closed
                window.location.reload()
                // For example, you could redirect the user:
                // window.location.href = '/another-page';
            });
        } else if (data.error) {
            // Show an error alert
            swal('Error', data.error, 'error');
        }
    } catch (error) {
        // Handle network or unexpected errors
        swal('Question Upload', `Something went wrong: ${error.message}`, 'error');
     
    }
});
