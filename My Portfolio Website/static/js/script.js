/* =====================================
   MOBILE MENU TOGGLE
===================================== */


const menuBtn = document.querySelector(".menu-btn");
const navLinks = document.querySelector(".nav-links");


menuBtn.addEventListener("click", () => {

    navLinks.classList.toggle("active");

    menuBtn.innerHTML = navLinks.classList.contains("active")
        ? '<i class="fa-solid fa-xmark"></i>'
        : '<i class="fa-solid fa-bars"></i>';

});





// Close menu after clicking navigation link

document.querySelectorAll(".nav-links a").forEach(link => {

    link.addEventListener("click", () => {

        navLinks.classList.remove("active");

        menuBtn.innerHTML =
        '<i class="fa-solid fa-bars"></i>';

    });

});







/* =====================================
   TYPING EFFECT
===================================== */


const typingText = document.querySelector(".typing");


const roles = [

    "Full Stack Developer",
    "Python Developer",
    "AI/ML Developer",
    "Web Developer",
    "Software Developer"

];


let roleIndex = 0;
let charIndex = 0;
let deleting = false;



function typingAnimation(){


    let currentRole = roles[roleIndex];


    if(!deleting){


        typingText.textContent =
        currentRole.substring(0,charIndex++);


        if(charIndex > currentRole.length){

            deleting = true;

            setTimeout(typingAnimation,1000);

            return;

        }


    }


    else{


        typingText.textContent =
        currentRole.substring(0,charIndex--);



        if(charIndex < 0){

            deleting=false;

            roleIndex++;

            if(roleIndex >= roles.length){

                roleIndex=0;

            }

        }


    }


    setTimeout(typingAnimation,100);

}


typingAnimation();









/* =====================================
   DARK / LIGHT THEME
===================================== */


const themeBtn = document.getElementById("theme-toggle");



themeBtn.addEventListener("click",()=>{


    document.body.classList.toggle("dark");



    const icon =
    themeBtn.querySelector("i");



    if(document.body.classList.contains("dark")){


        icon.classList.remove("fa-moon");

        icon.classList.add("fa-sun");


    }


    else{


        icon.classList.remove("fa-sun");

        icon.classList.add("fa-moon");


    }



});









/* =====================================
   ACTIVE NAVIGATION ON SCROLL
===================================== */


const sections =
document.querySelectorAll("section");


const navItems =
document.querySelectorAll(".nav-links a");



window.addEventListener("scroll",()=>{


    let current="";


    sections.forEach(section=>{


        const sectionTop =
        section.offsetTop - 150;



        if(scrollY >= sectionTop){

            current = section.getAttribute("id");

        }


    });



    navItems.forEach(link=>{


        link.classList.remove("active");


        if(link.getAttribute("href")
        === "#" + current){


            link.classList.add("active");


        }


    });



});









/* =====================================
   BACK TO TOP BUTTON
===================================== */


const topBtn =
document.getElementById("back-to-top");



window.addEventListener("scroll",()=>{


    if(window.scrollY > 400){


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









/* =====================================
   ANIMATED COUNTER
===================================== */


const counters =
document.querySelectorAll("[data-count]");



let counterStarted=false;



function startCounter(){


    const statsSection =
    document.querySelector(".stats");


    const position =
    statsSection.getBoundingClientRect().top;



    if(position < window.innerHeight
    && !counterStarted){



        counters.forEach(counter=>{


            let target =
            Number(counter.dataset.count);



            let count=0;



            let speed =
            target / 100;



            const updateCounter = ()=>{


                if(count < target){


                    count += speed;


                    counter.innerText =
                    Math.ceil(count);


                    setTimeout(updateCounter,20);


                }


                else{


                    counter.innerText=target;


                }


            };



            updateCounter();



        });



        counterStarted=true;


    }



}



window.addEventListener(
"scroll",
startCounter
);









/* =====================================
   CONTACT FORM VALIDATION
===================================== */


const contactForm =
document.getElementById("contact-form");



contactForm.addEventListener("submit",(e)=>{


    e.preventDefault();



    const name =
    document.getElementById("name").value.trim();



    const email =
    document.getElementById("email").value.trim();



    const message =
    document.getElementById("message").value.trim();




    if(name === "" ||
       email === "" ||
       message === ""){


        alert(
        "Please fill all required fields!"
        );


        return;


    }




    if(!email.includes("@")){


        alert(
        "Please enter a valid email!"
        );


        return;


    }




    alert(
    "Message sent successfully!"
    );



    contactForm.reset();



});









/* =====================================
   SCROLL REVEAL ANIMATION
===================================== */


const revealElements =
document.querySelectorAll(
".glass-card,.skill-card,.service-card"
);



function revealOnScroll(){



    revealElements.forEach(element=>{


        let position =
        element.getBoundingClientRect()
        .top;



        if(position < window.innerHeight-100){


            element.style.opacity="1";

            element.style.transform=
            "translateY(0)";


        }


    });


}



revealElements.forEach(element=>{


    element.style.opacity="0";

    element.style.transform=
    "translateY(40px)";

    element.style.transition=
    "0.6s ease";


});



window.addEventListener(
"scroll",
revealOnScroll
);



revealOnScroll();








/* =====================================
   SAVE THEME PREFERENCE
===================================== */


if(localStorage.getItem("theme")
==="dark"){


    document.body.classList.add("dark");


    themeBtn.querySelector("i")
    .classList.replace(
    "fa-moon",
    "fa-sun"
    );


}




themeBtn.addEventListener("click",()=>{


    if(document.body.classList.contains("dark")){


        localStorage.setItem(
        "theme",
        "dark"
        );


    }

    else{


        localStorage.setItem(
        "theme",
        "light"
        );


    }


});