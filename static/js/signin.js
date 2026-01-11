var signinbtn = document.querySelector('.signinbtn-txt')
var signinicon = document.querySelector('.signinicon')
const signinmodal= document.querySelector(".signinmodal");
 const signInModal = document.querySelector(".openModal");
 const mobilesignInModal = document.querySelector(".mobile-openModal");
 const signincloseModalBtn = document.querySelector("#signinclose");


/*-----------------------------------for signin moda; ------------------------------*/

    signInModal.addEventListener('click',  function() {

           signinmodal.style.display = "block"


    })
    signincloseModalBtn.addEventListener("click", function () {
      signinmodal.style.display = "none";

  });


/*-----------------------------------for mobile signin moda; ------------------------------*/

 mobilesignInModal.addEventListener('click',  function() {

    signinmodal.style.display = "block"


})
signincloseModalBtn.addEventListener("click", function () {
signinmodal.style.display = "none";

});


  document.addEventListener("DOMContentLoaded", function () {
    const usernameInput = document.getElementById('username');


    usernameInput.addEventListener('keydown', function (event) {
        if (event.key === " ") {

            event.preventDefault(); // Prevent space from being typed
        } else {

        }
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const usernameInput = document.getElementById('susername');


    usernameInput.addEventListener('keydown', function (event) {
        if (event.key === " ") {

            event.preventDefault(); // Prevent space from being typed
        } else {

        }
    });
});



/*------------------------------------signin refresh btn----------------------------------*/

$(document).on('submit', '#signinpage', function(e){
     signinbtn.innerHTML = ''
    signinicon.style.display="block"
    e.preventDefault();
    var formData = new FormData(this)


    $.ajax({
        type:'POST',
        url:'/signin',
        processData: false,
        contentType: false,
        data: formData,


  success: function(data){
    if ('success' in data) {
        setTimeout(()=>{
            signinbtn.innerHTML = 'Sign In '
            signinicon.style.display="none"
            window.location.replace(data.success)

        }, 1500)
    } else if('error' in data){
        setTimeout(()=>{
            signinbtn.textContent = 'Sign In '
            signinicon.style.display="none"
            swal('AUTHENTICATION', data.error, 'error' )




        }, 1000)
        // Handle other responses or errors

    }


  },


  error:function(data){
    setTimeout(()=>{

        signinbtn.innerHTML = 'Sign In '
        signinicon.style.display="none"

        swal('AUTHENTICATION', data.error, 'error' )




    }, 1000)



  }




    });


  })


//-----------------------------------------signup page ------------------------------------------
const btn =  document.querySelector('.signup-text')
const icon =  document.querySelector('.fa-spinner')


  $(document).on('submit', '#signuppage', function(e){
    e.preventDefault();
    var formData = new FormData(this)
    btn.innerHTML = ' '
    icon.style.display="block"

    $.ajax({
        type:'POST',
        url:'/signup',
        processData: false,
        contentType: false,
        data:  formData,

success: function(data){
    if ('success' in data){
        setTimeout(()=>{
            btn.innerHTML = 'Create Account'
            icon.style.display="none"
            swal('ACCOUNT CREATION', data.success, 'success')
            .then(() => {
                // Refresh the page after the OK button is clicked
                window.location.replace('/dashboard')
            });

            // Show the modal after redirect
        }, 1500)
    } else if ('error' in data) {
        setTimeout(()=>{

            btn.textContent = 'Create Account'
            icon.style.display="none"
            swal('Account Creation', data.error, 'error' )





        }, 1000)
        // Handle other responses or errors

    }


},


error:function(data){
    setTimeout(()=>{

        btn.textContent = 'Sign Up '
        icon.style.display="none"
        swal('Account Created', data.error, error)



    }, 1000)



}





});


})
//-------------------------------dropdown moounse------------------
const dropdown = document.querySelector('.dropdownonmouse');
const dropdownContent = document.querySelector('.dropdown-content');

// Toggle visibility on click
dropdown.addEventListener('click', () => {
    if (dropdownContent.style.display === 'block') {
        dropdownContent.style.display = 'none';
    } else {
        dropdownContent.style.display = 'block';
    }
});
