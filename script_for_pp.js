var loadFile = function (event) {
    var image = document.getElementById("output");
    image.src = URL.createObjectURL(event.target.files[0]);
};

document.getElementById('file').addEventListener('change', function () {
    var file = this.files[0];
    var reader = new FileReader();
    reader.onloadend = function () {
        document.getElementById('encoded_photo').value = reader.result;
    };
    reader.readAsDataURL(file);
});

// function validatePassword() {
//     var passwordRegex = /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$/;
//     var passwordInput = document.getElementById('password').value;

//     if (!passwordRegex.test(passwordInput)) {
//         alert('Please enter a valid phone number in the format +380XXXXXXXXX.');
//     }
// }

function toMainPage() {
    window.location.href = "/"
}
