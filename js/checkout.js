document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('payment-form');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();  // מונע טעינת דף מחדש
            const data = new FormData(form);  // יוצר אובייקט FormData מהטופס

            fetch('/process_payment', {
                method: 'POST',  // מבצע בקשת POST לכתובת /process_payment
                body: data  // שולח את הנתונים מהטופס
            })
            .then(response => response.json())  // ממיר את התגובה לפורמט JSON
            .then(result => {
                if (result.message === "Payment successful!") {
                    alert('Payment successful! Redirecting to homepage...');
                    resetCartDisplay();
                    setTimeout(() => {
                        window.location.href = '/';  // מנווט לעמוד הבית לאחר 2 שניות
                    }, 2000);
                } else {
                    alert('Payment failed. Please try again.');  // מציג הודעת כשלון
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Payment failed. Please try again.');  // מציג הודעת כשלון במקרה של שגיאה ברשת
            });
        });
    }

    function resetCartDisplay() {
        const cartList = document.getElementById('cart-list');
        cartList.innerHTML = '';
        document.getElementById('total-sum').textContent = '0.00';
        document.getElementById('cart-items').style.display = 'none';

        const cartButton = document.getElementById('cart-button');
        if (cartButton) {
            cartButton.textContent = 'עגלת קניות (0)';
        }
    }
});
