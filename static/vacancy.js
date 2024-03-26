function showMoreInfo(vacancyId, detailedId) {
    var vacancy = document.getElementById(vacancyId);
    var detailed = document.getElementById(detailedId);
    vacancy.style.display = 'none';
    detailed.style.display = 'flex';
    detailed.style.width = '300px !important';
}

function showLessInfo(vacancyId, detailedId) {
    var vacancy = document.getElementById(vacancyId);
    var detailed = document.getElementById(detailedId);
    vacancy.style.display = 'flex';
    detailed.style.display = 'none';
}

function toIndex() {
    window.location.href = '/'
}

// document.getElementById('searchInput').addEventListener('keypress', function(event) {
//     if (event.key === 'Enter') {
//         var searchQuery = this.value.trim().toLowerCase();
//         var oneVacancies = document.querySelectorAll('.one-vacancy');
//         oneVacancies.forEach(function(oneVacancy) {
//             var vacancyName = oneVacancy.querySelector('.vacancy p').textContent.trim().toLowerCase();
//             if (vacancyName.includes(searchQuery)) {
//                 oneVacancy.style.display = 'block';
//             } else {
//                 oneVacancy.style.display = 'none';
//             }
//         });
//     }
// });

// document.getElementById('searchInput').addEventListener('keypress', function(event) {
//     if (event.key === 'Enter') {
//         var searchQuery = this.value.trim().toLowerCase();
//         var oneVacancies = document.querySelectorAll('.one-vacancy');
//         oneVacancies.forEach(function(oneVacancy) {
//             var vacancyParagraphs = oneVacancy.querySelectorAll('.vacancy p');
//             var found = false;
//             vacancyParagraphs.forEach(function(paragraph) {
//                 var textContent = paragraph.textContent.trim().toLowerCase();
//                 if (textContent.includes(searchQuery)) {
//                     found = true;
//                 }
//             });
//             if (found) {
//                 oneVacancy.style.display = 'block';
//             } else {
//                 oneVacancy.style.display = 'none';
//             }
//         });
//     }
// });

document.getElementById('searchInput').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        var searchQuery = this.value.trim().toLowerCase();
        var oneVacancies = document.querySelectorAll('.one-vacancy');
        oneVacancies.forEach(function(oneVacancy) {
            var searchElements = oneVacancy.querySelectorAll('*[id="search-field"]');
            var found = false;
            searchElements.forEach(function(element) {
                var textContent = element.textContent.trim().toLowerCase();
                if (textContent.includes(searchQuery)) {
                    found = true;
                }
            });
            if (found) {
                oneVacancy.style.display = 'block';
            } else {
                oneVacancy.style.display = 'none';
            }
        });
    }
});

