    import {autoSaveExam}  from './save_exam.js'
    document.addEventListener('DOMContentLoaded', () => {
       
        const questionsContainer = document.getElementById('questions-container'); // Single parent container
        const addQuestionButton = document.getElementById('add-question');
        
        let questionCount = 0;
        
        addQuestionButton.addEventListener('click', () => {
            const questionCount = questionsContainer.querySelectorAll('.question-item').length + 1;
          

        
            const newQuestion = document.createElement('div');
            newQuestion.className = 'questions-builder';
            
            newQuestion.innerHTML = `
                <div class="question-item">
                    <p class="question-number">${questionCount}</p>
                    <input type="text" placeholder="Question Title ${questionCount}" class="question-title" required />
                    <select class="question-type" name="select-option">
                        <option value="multiple-choice">Multiple Choice</option>
                        <option value="short-answer">Short Answer</option>
                        <option value="paragraph">Paragraph</option>
                    </select>
                    <div class="question-options-container">
                        <div class="short-answer-options" style="border-bottom: 1px dashed grey; display: none;">
                        
                            <input type="text" placeholder="Enter short text answer" class="short-text-answer answer" required/>
                            

                        </div>
                        <div class="paragraph-options" style="border-bottom: 1px dashed grey; display: none;">
                         
                              <input type="text" placeholder="Enter paragraph text answer" class="paragraph-text-answer answer"  required/>
                        </div>
                        <div class="multiple-choice-options">
                            <div class="option-item">
                                <label class="option-label">
                                    <input type="radio" name="multiple-choice" class="option-radio" disabled />
                                    <input type="text" placeholder="Option 1" class="option-text" />
                                </label>
                                <button type="button" class="delete-option"><i class="fa-solid fa-xmark"></i></button>
                            </div>

                            <button class="add-option">+ Add Option</button>
                     <div class="select-answer">
                        <select class="select-answer-dropdown multichoice-answer"  required>
                            <option value="" disabled selected>Select Correct Answer</option>
                           
                        </select>
                        </div>
                    </select>
                        </div>
                    </div>
                    <button type="button" class="delete-question">Delete Question</button>
                </div>
            `;
        
            // Insert the new question before the Add Question button
            questionsContainer.insertBefore(newQuestion, addQuestionButton);
            updateQuestionButton()
            // Attach auto-save to input and change events for relevant elements
document.querySelectorAll("input, textarea, select, button").forEach((element) => {
    element.addEventListener("input", autoSaveExam);
    element.addEventListener("click", autoSaveExam);
});


            
        });
        
        // Event delegation for dynamic elements
        questionsContainer.addEventListener('change', (e) => {
            if (e.target.classList.contains('question-type')) {
                const questionItem = e.target.closest('.question-item');
                const optionsContainer = questionItem.querySelector('.question-options-container');

                // Hide all options
                optionsContainer.querySelectorAll('div').forEach(div => {
                    div.style.display = 'none';
                });
                
                // Show the selected option
                const selectedValue = e.target.value;
               
                optionsContainer.querySelectorAll('div').forEach(div => {
                    div.style.display = 'none';
                });
                if (selectedValue === 'short-answer') {
                    optionsContainer.querySelector('.short-answer-options').style.display = 'block';
                } else if (selectedValue === 'paragraph') {
                    optionsContainer.querySelector('.paragraph-options').style.display = 'block';
               
                } else if (selectedValue === 'multiple-choice') {
                  
                    optionsContainer.querySelector('.multiple-choice-options').style.display = 'block';
                    optionsContainer.querySelector('.select-answer').style.display = 'block';
                 
                } else if (selectedValue === 'checkbox') {
                    optionsContainer.querySelector('.checkbox-options').style.display = 'block';
                } else if (selectedValue === 'dropdown') {
                    optionsContainer.querySelector('.dropdown-options').style.display = 'block';
                }
            }
        });

        questionsContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('delete-question')) {
                // Find and remove the question item
                const questionItem = e.target.closest('.question-item');
                if (questionItem) {
                    questionItem.remove();
                }
        
                // Recalculate and update the numbering for remaining questions
                const remainingQuestions = questionsContainer.querySelectorAll('.question-item');
                remainingQuestions.forEach((question, index) => {
                    const questionNumberElement = question.querySelector('.question-number');
                    if (questionNumberElement) {
                        questionNumberElement.textContent = index + 1; // Update number (1-based index)
                    }
                });
        
                // Call autoSaveExam after deletion
                autoSaveExam();
                updateQuestionButton()
            }
        });
        


         // Function to populate the dropdown dynamically based on input values
         function updateAnswerOptions(questionElement) {
            const options = questionElement.querySelectorAll('.option-text');
            const selectDropdown = questionElement.querySelector('.select-answer-dropdown');
            
            // Clear existing options except the placeholder
            selectDropdown.innerHTML = '<option value="" disabled selected>Select Correct Answer</option>';
            
            // Add options dynamically
            options.forEach(option => {
              const value = option.value; // Get the value from the input
              if (value.trim() !== '') { // Only add if value is not empty
                const newOption = document.createElement('option');
                newOption.value = value;
                newOption.textContent = value;
                selectDropdown.appendChild(newOption);
              }
            });
          }
        
  // Event delegation for dynamic interaction
  document.addEventListener('input', (event) => {
    if (event.target.classList.contains('option-text')) {
      const questionElement = event.target.closest('.question-item');
      updateAnswerOptions(questionElement);
    }
  });

//-----------------------this is for adding option for mutichoice -----------------------------------------------
questionsContainer.addEventListener('click', (e) => {
    if (e.target.classList.contains('add-option')) {
        const multipleChoiceOptions = e.target.closest('.multiple-choice-options');

        if (multipleChoiceOptions) {
            const optionCount = multipleChoiceOptions.querySelectorAll('.option-item').length + 1;

            // Create a new option-item
            const newOption = document.createElement('div');
            newOption.className = 'option-item';

            newOption.innerHTML = `
                <label class="option-label">
                    <input type="radio" name="multiple-choice" class="option-radio" disabled />
                    <input type="text" placeholder="Option ${optionCount}" class="option-text" />
                </label>
                <button type="button" class="delete-option"><i class="fa-solid fa-xmark"></i></button>
            `;

            // Append the new option above the Add Option button
            multipleChoiceOptions.insertBefore(newOption, e.target);
           
             // Update option numbering
               // Update option numbering
                // Attach auto-save listener to the new input
            const newOptionInput = newOption.querySelector(".option-text");
            newOptionInput.addEventListener("input", autoSaveExam);
          
          
        }
    }


        });

//------------------------------update-question items------------------------------------


    // Function to update the button state based on the number of questions
    function updateQuestionButton() {
        const addButton = document.getElementById('add-question');
    const questionsContainer = document.getElementById('questions-container');
        const questionCount = questionsContainer.getElementsByClassName('question-item').length; // Get the current number of questions

        // Check if the subscription is inactive
        if (!subscriptionActive) {
            // If the subscription is inactive, control the button behavior
            if (questionCount < 10) {
                addButton.disabled = false; // Enable the button if fewer than 10 questions
                addButton.classList.remove('disabled'); // Remove disabled styles
            } else {
                addButton.disabled = true; // Disable the button if 10 or more questions
                addButton.classList.add('disabled'); // Add disabled styles
            }
        } else {
            // Disable the button if the subscription is active
           
            addButton.disabled = false; // Enable the button if the subscription is active
            addButton.classList.remove('disabled'); // Remove any disabled styles
        }
    }

    // Call the function to initialize the button state
updateQuestionButton();


//---------------------------this is for removing option for multi choice--------------------------------------------------

document.addEventListener('click', function (e) {
    // Check if the clicked element or its parent has the delete-option class
    const deleteItem = e.target.closest('.delete-option');

    if (deleteItem) {
        // Find the closest .option-item to remove
        const optionItem = deleteItem.closest('.option-item');

        // Find the closest question container (parent element holding options and dropdown)
        const questionElement = deleteItem.closest('.question-item');

        if (optionItem) {
            // Remove the option item
            optionItem.remove();

            // Update the dropdown dynamically
            if (questionElement) {
                updateAnswerOptions(questionElement);
            }

            // Auto-save and decrement option count
            autoSaveExam();
            optionCount--;

            console.log("Option deleted and dropdown updated.");
        }
    }
});

        

    
    });
    



