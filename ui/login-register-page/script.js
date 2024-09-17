const container = document.getElementById('container');
const regButton = document.getElementById('register');
const logButton = document.getElementById('login');

regButton.addEventListener('click', () => {
    container.classList.add("active");
})

logButton.addEventListener('click', () => {
    container.classList.remove("active");
})