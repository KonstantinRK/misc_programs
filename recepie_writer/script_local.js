function selectInfo(div_id) {

    var divsToHide = document.getElementsByClassName("step_field"); //divsToHide is an array
    for(var i = 0; i < divsToHide.length; i++){
       divsToHide[i].style.display = "none"; // depending on what you're doing
    }

    var buttons = document.getElementsByClassName("phase_button"); //divsToHide is an array
    for(var i = 0; i < buttons.length; i++){
       buttons[i].style.color = "black"; // depending on what you're doing
    }

    var ing = document.getElementsByClassName("ingredient_list"); //divsToHide is an array
    for(var i = 0; i < ing.length; i++){
        ing[i].style.display = "none";
    }



    var y = document.getElementById("button_"+div_id)
    y.style.color="green";

    var x = document.getElementsByClassName(div_id);
    for(var i = 0; i < x.length; i++){
        if (x[i].style.display === "none") {
            x[i].style.display = "block";

        } else {
            x[i].style.display = "none";
        }
    }



}