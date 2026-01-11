document.addEventListener("DOMContentLoaded", function() {
    // Attach event listeners to delete buttons
    document.querySelectorAll(".delete-response").forEach(function(button) {
        button.addEventListener("click", async function(event) {
            event.preventDefault(); // Prevent default link behavior
            
            const examId = this.getAttribute("exam-id"); // Get the exam ID
            const candidateId = this.getAttribute("data-id"); // Get the candidate ID
    
            try {
                // Send a POST request to the server for deletion
                const response = await fetch(`/delete_response/${examId}/${candidateId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value // CSRF token
                    }
                });

                // Parse the response
                const data = await response.json();
            

                if (response.ok && data.message) {
                    // Successfully deleted, remove the table
                    const table = document.getElementById(`table-${candidateId}`);
                    if (table) table.remove();

                } else {
                    // Handle errors returned by the server
                    alert(data.error || 'Failed to delete the exam response.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            }
        });
    });
});


document.addEventListener('DOMContentLoaded', () => {
    // Hide all sections by default
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });

    // Get the saved active section from local storage
    const savedSection = localStorage.getItem('activeSection');
    const defaultSectionId = savedSection ? savedSection : '#questions-section';
    const defaultSection = document.querySelector(defaultSectionId);

    // Display the saved or default section
    if (defaultSection) {
        defaultSection.style.display = 'block';
        // Update the URL without reloading
        history.replaceState({ section: defaultSectionId }, '', defaultSectionId);
    }

    // Set the active class on the corresponding nav link
    const defaultNavLink = document.querySelector(`.nav-link[href="${defaultSectionId}"]`);
    if (defaultNavLink) {
        defaultNavLink.classList.add('active');
    }

    // Add click event listeners to nav-links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default behavior
            const targetId = this.getAttribute('href');

            // Save the active section to local storage
            localStorage.setItem('activeSection', targetId);

            // Remove 'active' class from all nav links
            document.querySelectorAll('.nav-link').forEach(item => item.classList.remove('active'));

            // Add 'active' class to the clicked nav link
            this.classList.add('active');

            // Hide all content sections
            document.querySelectorAll('.content-section').forEach(section => {
                section.style.display = 'none';
            });

            // Display the target section
            const targetSection = document.querySelector(targetId);
            if (targetSection) {
                targetSection.style.display = 'block';
                // Update the URL without reloading the page
                history.pushState({ section: targetId }, '', targetId);
            }
        });
    });

    // Handle browser back/forward navigation
    window.addEventListener('popstate', (event) => {
        if (event.state && event.state.section) {
            // Hide all content sections
            document.querySelectorAll('.content-section').forEach(section => {
                section.style.display = 'none';
            });

            // Display the section from history state
            const targetSection = document.querySelector(event.state.section);
            if (targetSection) {
                targetSection.style.display = 'block';
            }

            // Update the active class on nav links
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            const activeLink = document.querySelector(`.nav-link[href="${event.state.section}"]`);
            if (activeLink) {
                activeLink.classList.add('active');
            }
        }
    });
});


document.addEventListener("DOMContentLoaded", () => {
    const openModalBtn = document.getElementById("open-modal"); // The publish button
    const closeModalBtn = document.getElementById("close-modal");
    const modal = document.getElementById("popup-modal");
    const copyButton = document.getElementById("copy-url");
    const copyMessage = document.getElementById("copy-message");
    const examUrlInput = document.getElementById("exam-url");
      // Copy URL to Clipboard
      copyButton.addEventListener("click", () => {
        examUrlInput.select();
        navigator.clipboard.writeText(examUrlInput.value).then(() => {
            copyMessage.style.display = "block";
            setTimeout(() => {
                copyMessage.style.display = "none";
            }, 1000);
        }).catch((err) => {
            console.error("Failed to copy URL:", err);
        });
    });


    // Close Modal
    closeModalBtn.addEventListener("click", () => {
        modal.style.display = "none";
    });

    // Close Modal when clicking outside the modal
    window.addEventListener("click", (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});

    // Function to fetch the publish exam URL from the server
    $(document).on('submit', '#publish-exam', function(e){
        const icon = document.querySelector('.fa-spinner')
        const pt = document.querySelector('.publishtext')
        const examUrlInput = document.getElementById("exam-url");
        const openModalBtn = document.querySelector(".popupmodal");
       
        e.preventDefault();
        icon.style.display = 'inline-block'
        pt.textContent='publishing..'
        var formData = new FormData(this);
        $.ajax({
            type:'POST',
            url:'/publish_exam',
            processData: false,
            contentType: false,
            data: formData,

            success: function(data){
                if ('success' in data) {
                    setTimeout(()=>{
                        examUrlInput.value= data.success
                        icon.style.display='none'
                        pt.textContent='Publish Exam'
                        openModalBtn.style.display="flex"
               
               
                       
                        
                        
                    }, 1000)}
                    else {
                        setTimeout(()=>{
                            icon.style.display = 'none'
                            pt.textContent='Publish Exam'
                            swal('PUBLISH EXAM', data.error, 'error')
                        
                            
                        }, 500)}
               
                 
                
                  
                },
               
               
               
               error:function(data){
                setTimeout(()=>{
               
                   
               icon.style.display = 'none'
               pt.textContent='Publish Exam'
               swal('PUBLISH EXAM', data.error, 'error')
               
                }, 1000)

            }

        })
                   
    })


  

$(document).on('submit', '#settingsForm', function(e){
    const settingsicon = document.querySelector('.settingsicon')
    const settingstext = document.querySelector('.settingtext')
    settingstext.innerHTML = 'saving...'
    settingsicon.style.display="inline-block"
   e.preventDefault();
   var formData = new FormData(this)
  
 
   $.ajax({
       type:'POST',
       url:'/my_exam_settings',
       processData: false,
       contentType: false,
       data: formData,
    
 
 success: function(data){
   if ('success' in data) {
       setTimeout(()=>{
           settingstext.innerHTML = 'Save Settings'
            settingsicon.style.display="none"
            swal('Exam Settings', data.success, 'success')
          
       }, 1500)
   } else {
       setTimeout(()=>{
            settingstext.innerHTML = 'Save Settings'
            settingsicon.style.display="none"
           //swal('Exam Settings', 'something went wrong', 'error' )
 
 
 
       }, 1000)
       // Handle other responses or errors
 
   }
 
 
 },
 
 
 error:function(data){
   setTimeout(()=>{
 
    settingstext.innerHTML = 'Save Settings'
    settingsicon.style.display="none"
   //swal('Exam Settings', 'something went wrong', 'error' )
 
 
 
   }, 1000)
 
 
 
 }
 
 
 
 
   });
 
 
 })


 document.querySelector('#exportData').addEventListener('submit', async (event) => {
    event.preventDefault();

    try {
        const examId = document.querySelector('.exam-id').value;
      

        const response = await fetch(`/export-to-excel/${examId}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to generate the file.');
        }

        const blob = await response.blob();
        const filename = response.headers.get('Content-Disposition').split('filename=')[1];

        // Create a download link
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename.replace(/"/g, ''); // Remove any quotes from the filename
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        alert('File downloaded successfully.');
    } catch (error) {
        alert(`Something went wrong: ${error.message}`);
        console.error('Error:', error);
    }
});


  
