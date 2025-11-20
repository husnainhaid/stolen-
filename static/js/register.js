document.getElementById("registerForm").addEventListener("submit", function (e) {
    const pw = document.getElementById("password").value;
    const cpw = document.getElementById("confirmPassword").value;

    if (pw !== cpw) {
        e.preventDefault();
        alert("Passwords do not match!");
    }
});
setTimeout(() => {
    const notes = document.querySelector('.flash-container');
    if (notes) notes.style.display = 'none';
}, 4000);