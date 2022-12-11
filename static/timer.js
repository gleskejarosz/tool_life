"use strict";

function padValue(number) {
    if (number < 10) {
        number = '0' + number
    }
    return number
}

function printDuration(duration){
    var seconds = Math.floor(duration)
    var minutes = Math.floor(seconds/60)
    var hours = Math.floor(minutes/60)
    seconds = seconds % 60
    minutes = minutes % 60
    if (hours) {
        return hours + ':' + padValue(minutes) + ':' + padValue(seconds)
    }
    return padValue(minutes) + ':' + padValue(seconds)
}

document.querySelectorAll('.django-timer-display').forEach( function(element){
    var duration = element.getAttribute('value')
    if (element.classList.contains('active')) {
        setInterval(function(){
            duration ++;
            element.innerHTML = printDuration(duration);
        }, 1000)
    }
    })

document.querySelectorAll('.django-timer-buttons button').forEach( function(element) {
    element.onclick = function(event){
        event.preventDefault()
        event.stopPropagation()
        var xhttp = new XMLHttpRequest()
        var url = element.getAttribute('formaction')
        var csrftoken = document.querySelector('.django-timer [name=csrfmiddlewaretoken]').getAttribute('value')
        xhttp.open("POST", url, true)
        xhttp.setRequestHeader("X-CSRFToken", csrftoken)
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4){
                if (this.status == 200){
                    window.location.reload()
                } else {
                    console.log(this)
                }
            }
        };
        xhttp.send()
    }
})
