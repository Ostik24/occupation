function showAddJobForm() {
    var addJobFormContainer = document.getElementById('addJobFormContainer');
    addJobFormContainer.style.display = "block";
}

function goBack() {
    // var personalInfoContainer = document.getElementById("personal-info-container");
    var personalEditContainer = document.getElementById("addJobFormContainer");

    // personalInfoContainer.style.display = "block";
    personalEditContainer.style.display = "none";
}

function goBackInfo(section) {
    var textContainer = document.getElementById(section + "-info-container");
    var formContainer = document.getElementById(section + "-edit-container");

    textContainer.style.display = "flex";
    formContainer.style.display = "none";
}
function toAddToCollection() {
    window.location.href = "/add_job_offer"
}

function goBackVacancy(vacancy, editing_vacancy) {
    var vacancyContainer = document.getElementById(vacancy);
    var editingContainer = document.getElementById(editing_vacancy);

    vacancyContainer.style.display = "flex";
    editingContainer.style.display = "none";
}

function signOut() {
    // Redirect to the sign-out route
    window.location.href = "/sign_out";
}

function deleter() {
    window.location.href = "/delete_account";
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

function vacancyDeleter(vacancyId) {
    if (confirm('Are you sure you want to delete this vacancy?')) {
        window.location.href = "/delete_vacancy?vacancy_id=" + vacancyId;
    }
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

function editVacancy(section) {
    var vacancyContainer = document.getElementById(section);
    var formContainer = document.getElementById('edit-' + section);

    vacancyContainer.style.display = "none";
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