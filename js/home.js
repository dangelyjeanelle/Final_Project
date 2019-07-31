const validateForm = () => {
  var x = document.forms["myForm"]["name"].value;
  if (x == "") {
    alert("Name must be filled out");
    return false;
  }
}

// let specialSection = document.getElementById('click')

// const hightlight = (text) => {
//   let
// }
