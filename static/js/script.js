
// ================= DARK MODE =================

const darkToggle = document.querySelector(".dark-toggle");

if (darkToggle) {

    darkToggle.addEventListener("click", () => {

        document.body.classList.toggle("dark-mode");

    });

}

// ================= MOBILE MENU =================

const mobileBtn = document.querySelector(".mobile-menu-btn");

const navLinks = document.querySelector(".nav-links");

if (mobileBtn) {

    mobileBtn.addEventListener("click", () => {

        navLinks.classList.toggle("active");

    });

}

// ================= POPUP NOTIFICATION =================

function showNotification(message) {

    const notification = document.createElement("div");

    notification.classList.add("notification");

    notification.innerText = message;

    document.body.appendChild(notification);

    setTimeout(() => {

        notification.remove();

    }, 2500);

}

// ================= PRODUCT SEARCH =================

const searchInput = document.querySelector("#searchInput");

if (searchInput) {

    searchInput.addEventListener("keyup", () => {

        let filter = searchInput.value.toLowerCase();

        let cards = document.querySelectorAll(".product-card");

        cards.forEach(card => {

            let title = card.querySelector("h3")
                            .innerText
                            .toLowerCase();

            if (title.includes(filter)) {

                card.style.display = "block";

            }

            else {

                card.style.display = "none";

            }

        });

    });

}

// ================= CATEGORY FILTER =================

const filterButtons = document.querySelectorAll(".filter-btn");

filterButtons.forEach(button => {

    button.addEventListener("click", () => {

        filterButtons.forEach(btn => {

            btn.classList.remove("active");

        });

        button.classList.add("active");

        let category = button.getAttribute("data-category");

        let cards = document.querySelectorAll(".product-card");

        cards.forEach(card => {

            if (
                category === "all" ||
                card.getAttribute("data-category") === category
            ) {

                card.style.display = "block";

            }

            else {

                card.style.display = "none";

            }

        });

    });

});

// ================= WISHLIST =================

const wishlistButtons =
document.querySelectorAll(".wishlist-btn");

wishlistButtons.forEach(button => {

    // Check on page load
    let wishlist =
    JSON.parse(localStorage.getItem("wishlist"))
    || [];

    const exists =
    wishlist.find(item =>
        item.name === button.dataset.name
    );

    if(exists){

        button.classList.add("wishlisted");
        button.innerHTML = "🩷";

    }

    button.addEventListener("click", () => {

        let product = {

            name: button.dataset.name,
            price: button.dataset.price,
            image: button.dataset.image,
            category: button.dataset.category,
            description: button.dataset.description

        };

        let wishlist =
        JSON.parse(localStorage.getItem("wishlist"))
        || [];

        const existingIndex =
        wishlist.findIndex(item =>
            item.name === product.name
        );

        // REMOVE FROM WISHLIST
        if(existingIndex !== -1){

            wishlist.splice(existingIndex, 1);

            localStorage.setItem(
                "wishlist",
                JSON.stringify(wishlist)
            );

            button.classList.remove("wishlisted");
            button.innerHTML = "🤍";

            showNotification(
                "Removed From Wishlist"
            );

            return;
        }

        // ADD TO WISHLIST
        wishlist.push(product);

        localStorage.setItem(
            "wishlist",
            JSON.stringify(wishlist)
        );

        button.classList.add("wishlisted");

        button.innerHTML = "🩷";

        button.style.transform =
        "scale(1.15)";

        setTimeout(() => {

            button.style.transform =
            "scale(1)";

        },300);

        showNotification(
            "Added To Wishlist ❤️"
        );

    });

});
// ================= CART =================

const cartButtons =
document.querySelectorAll(".cart-btn");

cartButtons.forEach(button => {

    button.addEventListener("click", () => {

        const productCard =
        button.closest(".product-card");

        const product = {

            name:
            productCard.querySelector("h3")
            .innerText,

           price:
parseInt(
    productCard.querySelector(".product-price")
    .innerText.replace("₹","")
),

            image:
            productCard.querySelector("img").src,

            category:
            productCard.querySelector(".product-category")
            .innerText,

            description:
            productCard.querySelector("p")
            .innerText,

            quantity:1

        };

        let cart =
        JSON.parse(
            localStorage.getItem("cart")
        ) || [];

        const existing =
        cart.find(item =>
            item.name === product.name
        );

        if(existing){

            existing.quantity++;

        }

        else{

            cart.push(product);

        }

        localStorage.setItem(
            "cart",
            JSON.stringify(cart)
        );

        updateCartCount();

        button.innerHTML =
        "✓ Added";

        button.style.background =
        "#d98bb4";

        button.style.color =
        "white";

        button.style.transform =
        "scale(1.08)";

        setTimeout(() => {

            button.innerHTML =
            "Add To Cart";

            button.style.background =
            "";

            button.style.color =
            "";

            button.style.transform =
            "scale(1)";

        },1500);

        showNotification("Added To Cart 🛒");

    });

});

// ================= CART COUNT =================

function updateCartCount(){

    const cartBadges =
    document.querySelectorAll(".cart-count");

    let cart =
    JSON.parse(localStorage.getItem("cart"))
    || [];

    let total = 0;

    cart.forEach(item => {

        total += item.quantity || 1;

    });

    cartBadges.forEach(badge => {

        badge.textContent = total;

        if(total > 0){

            badge.style.display = "flex";

        }
        else{

            badge.style.display = "none";

        }

    });

}// ================= SMOOTH SCROLL =================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        e.preventDefault();

        document.querySelector(
            this.getAttribute("href")
        ).scrollIntoView({

            behavior: "smooth"

        });

    });

});
// ================= ADD WISHLIST ITEM TO CART =================

function addWishlistItemToCart(index){

    let wishlist =
    JSON.parse(localStorage.getItem("wishlist"))
    || [];

    let cart =
    JSON.parse(localStorage.getItem("cart"))
    || [];

    const product = wishlist[index];

    const existing =
    cart.find(item =>
        item.name === product.name
    );

    if(existing){

        existing.quantity =
        (existing.quantity || 1) + 1;

    }
    else{

        cart.push({
            ...product,
            quantity: 1
        });

    }

    localStorage.setItem(
        "cart",
        JSON.stringify(cart)
    );

    // remove from wishlist
    wishlist.splice(index,1);

    localStorage.setItem(
        "wishlist",
        JSON.stringify(wishlist)
    );

    showNotification(
        "Added To Cart 🛒"
    );

    location.reload();
}
function updateWishlistCount(){

    const wishlistBadges =
    document.querySelectorAll(".wishlist-count");

    let wishlist =
    JSON.parse(localStorage.getItem("wishlist"))
    || [];

    wishlistBadges.forEach(badge => {

        badge.textContent = wishlist.length;

        if(wishlist.length > 0){

            badge.style.display = "flex";

        }
        else{

            badge.style.display = "none";

        }

    });

}

const profileToggle = document.querySelector(".profile-toggle");
const profileMenu = document.querySelector(".profile-menu");

if (profileToggle && profileMenu) {
    profileToggle.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        profileMenu.classList.toggle("active");
    });

    document.addEventListener("click", (e) => {
        if (!profileMenu.contains(e.target) && !profileToggle.contains(e.target)) {
            profileMenu.classList.remove("active");
        }
    });
}
updateWishlistCount();
// ================= INITIAL LOAD =================

updateCartCount();