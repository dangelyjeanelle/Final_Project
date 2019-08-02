const validateForm = () => {
  var x = document.forms["myForm"]["name"].value;
  if (x == "") {
    alert("Name must be filled out");
    return false;
  }
}

let keyPressed = document.querySelectorAll('key');
let slideIndex = 1;
const showDivs = (n) => {
  let i;
  let x = [...document.querySelectorAll(".mySlide")];
  if (n > x.length) {
    slideIndex = 1;
  }
  if (n < 1) {
    slideIndex = x.length;
  }
  for (i = 0; i < x.length; i++) {
    x[i].classList.add('hidden');
    x[i].classList.remove('active');

  }
  x[slideIndex-1].classList.add('active');
  x[slideIndex-1].classList.remove('hidden');

  let leftIndex = (slideIndex + x.length - 1) % x.length;
  let rightIndex = (slideIndex + x.length + 1) % x.length;
  x[leftIndex].classList.add('left');
  x[rightIndex].classList.add('right');
}
showDivs(slideIndex);
const plusDivs = (n) => {
  showDivs(slideIndex += n);
}

document.addEventListener('keydown', (e) => {
  if (e.key === "ArrowRight") {
    plusDivs(1);
  } else if (e.key === "ArrowLeft") {
    plusDivs(-1);
  }
});

// let deleteLink = document.querySelectorAll('delete');
// const confirmation = () => {
//   if (confirm("Are you sure you want to delete this account permanently?") {
//     alert("Your account is deleted");
  // }else {

//   }
// };
  // function JSconfirm(){
  // 	swal({
  //     title: "Redirect to main page!",
  //     text: "Redirect me to home page?",
  //     type: "warning",
  //     showCancelButton: true,
  //     confirmButtonColor: "#DD6B55",
  //     confirmButtonText: "Yes",
  //     cancelButtonText: "No",
  //     closeOnConfirm: false,
  //     closeOnCancel: false },
  //     function(isConfirm){
  //         if (isConfirm)
  //     {
  //         window.location = "https://www.jquery-az.com/";
  //         }
  //         else {
  //             swal("You are not redirected!", "success");
  //             } });
  // }
