let currentSlide = 1;
const totalSlides = 3;

function moveSlide(direction) {
    currentSlide += direction;
    if (currentSlide < 1) {
        currentSlide = totalSlides;
    } else if (currentSlide > totalSlides) {
        currentSlide = 1;
    }
    document.getElementById(`slide${currentSlide}`).checked = true;
}

// Automatic slide every 5 seconds
setInterval(() => {
    moveSlide(1);
}, 5000);
