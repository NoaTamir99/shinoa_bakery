document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('form').addEventListener('submit', function(event) {
        const inputs = document.querySelectorAll('input[type="text"]');
        let valid = true;

        inputs.forEach(input => {
            if (input.value === '') {
                valid = false;
            }
        });

        if (!valid) {
            event.preventDefault();
            alert('אנא מלאו את כל השדות');
        }
    });
});
