const validateForm = () => {
  var x = document.forms["myForm"]["name"].value;
  if (x == "") {
    alert("Name must be filled out");
    return false;
  }
}

let slideIndex = 1;
showDivs(slideIndex);

const plusDivs(n) {
  showDivs(slideIndex += n);
}

const showDivs(n) {
  let i;
  let x = document.getElementByClassName("mySlide");
  if (n > x.length) {
    slideIndex = 1;
  }
  if (n < 1) {
    slideIndex = x.length;
  }
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  x[slideIndex-1].style.display = "block";
}
