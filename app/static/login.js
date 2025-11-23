// Simple logic for modal, fake "register", form and animation
function openForgotModal() {
  document.getElementById('forgotModal').style.display = "flex";
  setTimeout(function() {
    document.querySelector('.forgot-modal-content').style.animation = "modalIn 0.43s cubic-bezier(0.68, -0.55, 0.27, 1.55)";
  }, 20);
}
function closeForgotModal() {
  document.getElementById('forgotModal').style.display = "none";
  document.getElementById('resetMessage').textContent = "";
  document.getElementById('forgotUserID').value = "";
}
function registerAccount() {
  alert("Redirect to Register page, or open register modal here.");
}
function sendResetLink() {
  var input = document.getElementById('forgotUserID').value.trim();
  var msg = document.getElementById('resetMessage');
  if(!input) {
    msg.style.color = "crimson";
    msg.textContent = "Please enter your User ID!";
    return;
  }
  msg.style.color = "mediumseagreen";
  msg.textContent = "A password reset instruction will be sent if this User ID exists.";
}
document.querySelector('.login-form').addEventListener('submit', function(e){
  e.preventDefault();
  var userID = document.getElementById('userID').value.trim();
  var pwd = document.getElementById('password').value.trim();
  if(!userID || !pwd)
    return;
  document.getElementById('loginCard').classList.add('animate-login-success');
  setTimeout(function(){
    alert("Demo only:\nUserID: " + userID + "\nPassword: " + pwd + "\n(You may redirect, validate or call API here!)");
    document.getElementById('loginCard').classList.remove('animate-login-success');
  },500);
});

// Animate login card on submit
const style = document.createElement('style');
style.innerHTML = `
.animate-login-success {
  animation: loginSuccess 0.5s forwards;
}
@keyframes loginSuccess {
  0% { box-shadow: 0 10px 32px 0 rgba(39, 0, 120, 0.2);}
  40% { transform: scale(1.03) rotate(-1deg);}
  60% { box-shadow: 0 20px 50px 0 rgba(93, 232, 245, 0.22);}
  100% { box-shadow: 0 6px 16px 0 rgba(39, 0, 120, 0.10); transform: scale(1);}
}`;
document.head.appendChild(style);
