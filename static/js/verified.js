btn = document.querySelector('#resend-text')
icon = document.querySelector('.resendbtn-spinner')
notificationText = document.querySelector('.notification')


$(document).on('click', '#verification', function(e){
e.preventDefault();
 btn.textContent = ' '
 icon.style.display="inline-block"

$.ajax({
    type:'POST',
    url:'/resend-verification',
    data:{
        csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
    },

success: function(data){
if ('success' in data) {
    setTimeout(()=>{
        btn.textContent = 'resend '
        icon.style.display="none"
        notificationText.innerHTML ='Email verification link has being sent to your mail\nkindly check your mail to activate your account'

         // Show the modal after redirect
    }, 3000)
} else {
    setTimeout(()=>{

        btn.textContent = 'resend '
        icon.style.display="none"
        notificationText.innerHTML=data.error 
        



    }, 1000)
    // Handle other responses or errors
  
}


},


error:function(data){
setTimeout(()=>{

    btn.textContent = 'Sign Up '
    icon.style.display="none"
    notificationText.innerHTML='something went wrong'





}, 1000)



}




});


})




