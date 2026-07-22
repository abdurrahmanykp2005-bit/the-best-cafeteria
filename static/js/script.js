/*==================================================
        THE BEST CAFETERIA
        PROFESSIONAL SCRIPT.JS
==================================================*/

"use strict";

/*==================================================
        GLOBAL VARIABLES
==================================================*/

const navbar = document.querySelector(".navbar");
const menuIcon = document.querySelector(".menu-icon");
const navLinks = document.querySelector(".nav-links");

const searchInput = document.getElementById("searchInput");

const featuredContainer = document.getElementById("featured-container");

const cartCount = document.getElementById("cart-count");

const themeButton = document.getElementById("theme-btn");

const lightbox = document.getElementById("lightbox");
const lightboxImage = document.getElementById("lightbox-img");

let cart = JSON.parse(localStorage.getItem("cart")) || [];

/*==================================================
        PAGE LOAD
==================================================*/

document.addEventListener("DOMContentLoaded", () => {

    console.log("Welcome To The Best Cafeteria");

    initializeTheme();

    initializeNavigation();

    initializeScrollAnimation();

    initializeBackToTop();

    loadMenu();

    updateCartCount();

});

/*==================================================
        MOBILE MENU
==================================================*/

function initializeNavigation(){

    if(!menuIcon) return;

    menuIcon.addEventListener("click",()=>{

        navLinks.classList.toggle("active");

    });

    document.querySelectorAll(".nav-links a").forEach(link=>{

        link.addEventListener("click",()=>{

            navLinks.classList.remove("active");

        });

    });

}

/*==================================================
        STICKY NAVBAR
==================================================*/

window.addEventListener("scroll",()=>{

    if(!navbar) return;

    if(window.scrollY>60){

        navbar.classList.add("sticky");

    }

    else{

        navbar.classList.remove("sticky");

    }

});

/*==================================================
        SMOOTH SCROLL
==================================================*/

document.querySelectorAll('a[href^="#"]').forEach(anchor=>{

    anchor.addEventListener("click",function(e){

        e.preventDefault();

        const target=document.querySelector(this.getAttribute("href"));

        if(target){

            target.scrollIntoView({

                behavior:"smooth"

            });

        }

    });

});

/*==================================================
        DARK MODE
==================================================*/

function initializeTheme(){

    const savedTheme=localStorage.getItem("theme");

    if(savedTheme==="light"){

        document.body.classList.add("light");

        if(themeButton){

            themeButton.innerHTML="☀️";

        }

    }

    if(themeButton){

        themeButton.addEventListener("click",toggleTheme);

    }

}

function toggleTheme(){

    document.body.classList.toggle("light");

    if(document.body.classList.contains("light")){

        localStorage.setItem("theme","light");

        themeButton.innerHTML="☀️";

    }

    else{

        localStorage.setItem("theme","dark");

        themeButton.innerHTML="🌙";

    }

}

/*==================================================
        SEARCH FOOD
==================================================*/

if(searchInput){

    searchInput.addEventListener("keyup",searchFood);

}

function searchFood(){

    const value=searchInput.value.toLowerCase();

    const cards=document.querySelectorAll(".searchable");

    cards.forEach(card=>{

        const name=card.querySelector("h3").textContent.toLowerCase();

        if(name.includes(value)){

            card.style.display="block";

        }

        else{

            card.style.display="none";

        }

    });

}

/*==================================================
        LIGHTBOX
==================================================*/

function openImage(src){

    if(!lightbox) return;

    lightbox.style.display="flex";

    lightboxImage.src=src;

}

function closeImage(){

    if(lightbox){

        lightbox.style.display="none";

    }

}

window.openImage=openImage;
window.closeImage=closeImage;

/*==================================================
        SCROLL ANIMATION
==================================================*/

function initializeScrollAnimation(){

    const sections=document.querySelectorAll("section");

    const observer=new IntersectionObserver(entries=>{

        entries.forEach(entry=>{

            if(entry.isIntersecting){

                entry.target.classList.add("show");

            }

        });

    },{

        threshold:.2

    });

    sections.forEach(section=>{

        section.classList.add("hidden");

        observer.observe(section);

    });

}

/*==================================================
        BACK TO TOP
==================================================*/

function initializeBackToTop(){

    const topBtn=document.getElementById("topBtn");

    if(!topBtn) return;

    window.addEventListener("scroll",()=>{

        if(window.scrollY>350){

            topBtn.style.display="block";

        }

        else{

            topBtn.style.display="none";

        }

    });

    topBtn.addEventListener("click",()=>{

        window.scrollTo({

            top:0,

            behavior:"smooth"

        });

    });

}

/*==================================================
        LOAD MENU FROM FLASK
==================================================*/

async function loadMenu() {

    if (!featuredContainer) return;

    try {

        const response = await fetch("/menu");

        if (!response.ok) {
            throw new Error("Failed to load menu.");
        }

        const menu = await response.json();

        featuredContainer.innerHTML = "";

        menu.forEach(item => {

            featuredContainer.innerHTML += `
                <div class="food-card searchable">

                    <img src="/static/images/${item.image}"
                         alt="${item.food_name}"
                         onclick="openImage(this.src)">

                    <div class="food-info">

                        <h3>${item.food_name}</h3>

                        <div class="price">
                            ₹${item.price}
                        </div>

                        <p>${item.description}</p>

                        <button class="order-btn-card"
                            onclick="addToCart({
                                id: ${item.id},
                                name: '${item.food_name}',
                                price: ${item.price},
                                image: '${item.image}',
                                quantity: 1
                            })">
                            Add To Cart
                        </button>

                    </div>

                </div>
            `;

        });

    } catch (error) {

        console.error("Menu Loading Error:", error);

    }

}
/*==================================================
        SHOPPING CART
==================================================*/

function addToCart(item){

    const existing = cart.find(food => food.name === item.name);

    if(existing){

        existing.quantity++;

    }

    else{

        item.quantity = 1;

        cart.push(item);

    }

    saveCart();

    updateCartCount();

    alert(item.name + " added to cart.");

}

/*==================================================
        SAVE CART
==================================================*/

function saveCart(){

    localStorage.setItem("cart",JSON.stringify(cart));

}

/*==================================================
        UPDATE CART COUNT
==================================================*/

function updateCartCount(){

    if(!cartCount) return;

    let total = 0;

    cart.forEach(item=>{

        total += item.quantity;

    });

    cartCount.textContent = total;

}

/*==================================================
        LOAD CART PAGE
==================================================*/

function loadCart(){

    const cartItems=document.getElementById("cart-items");

    const totalPrice=document.getElementById("cart-total");

    if(!cartItems) return;

    cartItems.innerHTML="";

    let total=0;

    if(cart.length===0){

        cartItems.innerHTML="<h2>Your cart is empty.</h2>";

        if(totalPrice){

            totalPrice.textContent="0";

        }

        return;

    }

    cart.forEach((item,index)=>{

        total += item.price * item.quantity;

        cartItems.innerHTML += `

        <div class="cart-item">

            <img src="/static/images/${item.image}">

            <div class="cart-details">

                <h3>${item.name}</h3>

                <p>₹${item.price}</p>

                <p>

                    Quantity

                    <button onclick="decreaseQuantity(${index})">-</button>

                    ${item.quantity}

                    <button onclick="increaseQuantity(${index})">+</button>

                </p>

            </div>

            <button class="remove-btn"

                onclick="removeFromCart(${index})">

                Remove

            </button>

        </div>

        `;

    });

    if(totalPrice){

        totalPrice.textContent=total;

    }

}

/*==================================================
        INCREASE QUANTITY
==================================================*/

function increaseQuantity(index){

    cart[index].quantity++;

    saveCart();

    updateCartCount();

    loadCart();

}

/*==================================================
        DECREASE QUANTITY
==================================================*/

function decreaseQuantity(index){

    if(cart[index].quantity>1){

        cart[index].quantity--;

    }

    else{

        cart.splice(index,1);

    }

    saveCart();

    updateCartCount();

    loadCart();

}

/*==================================================
        REMOVE ITEM
==================================================*/

function removeFromCart(index){

    cart.splice(index,1);

    saveCart();

    updateCartCount();

    loadCart();

}

/*==================================================
        CHECKOUT
==================================================*/

function checkout() {

    if (cart.length === 0) {
        alert("Your cart is empty.");
        return;
    }

    window.location.href = "/checkout";
}

/*==================================================
        CLEAR CART
==================================================*/

function clearCart(){

    cart=[];

    saveCart();

    updateCartCount();

    loadCart();

}

/*==================================================
        EXPOSE FUNCTIONS
==================================================*/

window.addToCart=addToCart;

window.removeFromCart=removeFromCart;

window.increaseQuantity=increaseQuantity;

window.decreaseQuantity=decreaseQuantity;

window.loadCart=loadCart;

window.checkout=checkout;

window.clearCart=clearCart;

/*==================================================
        FINAL INITIALIZATION
==================================================*/

document.addEventListener("DOMContentLoaded",()=>{

    updateCartCount();

    loadCart();

});