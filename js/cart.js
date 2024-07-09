let cart = [];

document.addEventListener('DOMContentLoaded', function() {
    // Fetch cart from the server when the page loads
    fetch('/cart')
        .then(response => response.json())
        .then(data => {
            cart = data;
            updateCartDisplay();
        });

    document.getElementById('cart-button').addEventListener('click', function() {
        const cartItems = document.getElementById('cart-items');
        cartItems.style.display = cartItems.style.display === 'none' ? 'block' : 'none';
    });

    function addToCart(item, price) {
        const cartItem = cart.find(i => i.name === item);
        if (cartItem) {
            cartItem.quantity++;
        } else {
            cart.push({ name: item, price: price, quantity: 1 });
        }
        updateCartDisplay();
        saveCart();
    }

    function removeFromCart(item) {
        const cartItem = cart.find(i => i.name === item);
        if (cartItem) {
            cartItem.quantity--;
            if (cartItem.quantity <= 0) {
                const index = cart.indexOf(cartItem);
                cart.splice(index, 1);
            }
        }
        updateCartDisplay();
        saveCart();
    }

    function updateCartDisplay() {
        const cartList = document.getElementById('cart-list');
        cartList.innerHTML = '';
        let totalSum = 0;
        cart.forEach(item => {
            const li = document.createElement('li');
            li.textContent = `${item.name} - ${item.quantity} x $${item.price.toFixed(2)}`;
            cartList.appendChild(li);
            totalSum += item.price * item.quantity;
        });
        document.getElementById('total-sum').textContent = totalSum.toFixed(2);
        document.getElementById('cart-items').style.display = cart.length > 0 ? 'block' : 'none';
    }

    function saveCart() {
        fetch('/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cart: cart }),
        })
        .then(response => response.json())
        .then(data => console.log(data.message));
    }

    // Export functions to be used in other scripts if needed
    window.addToCart = addToCart;
    window.removeFromCart = removeFromCart;
});
