const userBtn = document.getElementById("userBtn");
const adminBtn = document.getElementById("adminBtn");
const roleInput = document.getElementById("roleInput");
const loginForm = document.getElementById("loginForm");

// Toggle button logic
userBtn.onclick = () => {
    userBtn.classList.add("active");
    adminBtn.classList.remove("active");
    roleInput.value = "user";
};

adminBtn.onclick = () => {
    adminBtn.classList.add("active");
    userBtn.classList.remove("active");
    roleInput.value = "admin";
};

loginForm.addEventListener("submit", function (e) {
  

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    // alert(`Hello, ${email}!\nRole: ${roleInput.value}\nPassword: ${password}`);
});
setTimeout(() => {
    const notes = document.querySelector('.notifications');
    if (notes) notes.style.display = 'none';
}, 4000);
