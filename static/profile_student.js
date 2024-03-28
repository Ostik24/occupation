function signOut() {
    // Redirect to the sign-out route
    window.location.href = "/sign_out";
}

function deleter() {
    // Redirect to the sign-out route
    window.location.href = "/delete_account";
}

function to_index() {
    // Redirect to the sign-out route
    window.location.href = "/";
}

function editButton(section) {
    var textContainer = document.getElementById(section + "-info-container");
    var formContainer = document.getElementById(section + "-edit-container");

    textContainer.style.display = "none";
    formContainer.style.display = "block";
}
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

function autoResize(element) {
    element.style.height = "auto";
    element.style.height = (element.scrollHeight) + "px";
}

function goBackInfo(section) {
var textContainer = document.getElementById(section + "-info-container");
var formContainer = document.getElementById(section + "-edit-container");

textContainer.style.display = "flex";
formContainer.style.display = "none";
}

// Get the modal element
const modal = document.getElementById('myModal');

// Function to open the modal
function openModal() {
    modal.style.display = 'block';
}

// Function to close the modal
function closeModal() {
    modal.style.display = 'none';
}

// Close the modal when the "No!" button is clicked
const noButton = document.querySelector('.modal-content .out-button');
noButton.addEventListener('click', closeModal);

// Prevent closing the modal by clicking outside of it
modal.addEventListener('click', function(event) {
    if (event.target === modal) {
        closeModal(); // Close modal only if clicked on the modal background
    }
});

function validateAge() {
    var ageInput = document.getElementById('edit-age').value;
    var age = parseInt(ageInput);

    if (age < 16 || age > 120) {
        alert('Age must be between 16 and 120.');
    }
}


function validatePhoneNumber() {
    var phoneNumberInput = document.getElementById('edit-phone').value;
    var regex = /^\+380\d{9}$/;

    if (phoneNumberInput.trim() === '') {
        // Input is empty, so it's okay
        return true;
    } else {
        // Input is not empty, validate against regex
        if (!regex.test(phoneNumberInput)) {
            alert('Please enter a valid phone number in the format +380XXXXXXXXX.');
            return false;
            // document.getElementById('edit-phone').value = ''; // Clear the input field
        }
        return true;
    }
}

function validateEnglishLevel() {
    var englishLevelInput = document.getElementById('edit-english').value;
    var regex = /^([ABCabc][1-2])((\+){0,1})$/;

    if (!englishLevelInput) {
        return true;
    }

    if (!regex.test(englishLevelInput)) {
        alert('Please make sure to provide a valid English level in the correct format (e.g., A2+).');
        return false;
    }
    return true;
}
