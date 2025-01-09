// Initialize DataTables on the ranking table
$(document).ready(function () {
    $('#rankingTable').DataTable({
        "pageLength": 5 // Show 5 rows per page by default
    });
});

function submitChoice(winner, loser) {
    fetch('/submit_choice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ winner, loser })
    })
        .then(response => response.json())
        .then(data => location.reload())
        .catch(err => alert('Error submitting choice.'));
}

function showPopup(src) {
    const popup = document.getElementById('imagePopup');
    popup.style.display = 'flex';
    popup.querySelector('img').src = src;
}

function hidePopup() {
    const popup = document.getElementById('imagePopup');
    popup.style.display = 'none';
    popup.querySelector('img').src = '';
}

document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        hidePopup();
    }
});

async function fetchWikidataLabels() {
    const items = document.querySelectorAll('.wikidata-item');
    const ids = Array.from(items).map(item => item.getAttribute('data-id'));

    if (ids.length > 0) {
        const url = `https://www.wikidata.org/w/api.php?action=wbgetentities&ids=${ids.join('|')}&format=json&languages=en&props=labels&origin=*`;
        try {
            const response = await fetch(url);
            const data = await response.json();
            items.forEach(item => {
                const id = item.getAttribute('data-id');
                const label = data.entities[id]?.labels?.en?.value || id;
                item.textContent = label;
            });
        } catch (error) {
            console.error('Error fetching labels from Wikidata:', error);
        }
    }
}

window.onload = fetchWikidataLabels;
