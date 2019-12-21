
function selectVersion(version_group) {

    var divsToHide = document.getElementsByClassName('main_container'); //divsToHide is an array
    for(var j = 0; j < divsToHide.length; j++){
         divsToHide[j].style.display = "none"; // depending on what you're doing
   }

    var button = document.getElementsByClassName('version_button');
    for(var i = 0; i < button.length; i++){
        button[i].style.background = "white"; // depending on what you're doing
        button[i].style.color = "black";
    }

   var y = document.getElementById("button_"+version_group);
   y.style.background="green";
   y.style.background.hover="green";
   y.style.color = "white";

   var divsToShow = document.getElementsByClassName(version_group);
   for(var i = 0; i < divsToShow.length; i++){
       if (divsToShow[i].style.display === "none") {
           divsToShow[i].style.display = "flex";
       } else {
           divsToShow[i].style.display = "none";
       }
   }
}

function unfade(element) {
    var op = 0.1;  // initial opacity
    element.style.display = 'block';
    var timer = setInterval(function () {
        if (op >= 1){
            clearInterval(timer);
        }
        element.style.opacity = op;
        element.style.filter = 'alpha(opacity=' + op * 100 + ")";
        op += op * 0.1;
    }, 50);
}

function fade(element) {
    var op = 1;  // initial opacity
    var timer = setInterval(function () {
        if (op <= 0.1){
            clearInterval(timer);
            element.style.display = 'none';
        }
        element.style.opacity = op;
        element.style.filter = 'alpha(opacity=' + op * 100 + ")";
        op -= op * 0.1;
    }, 3);
}