document.getElementById('expiry-date').addEventListener('input', function(e) {
    let value = e.target.value;
    if (value.length === 2 && !value.includes('/')) {
        e.target.value = value + '/';
    }
});
