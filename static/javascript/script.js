var theme = window.localStorage.currentTheme;

$("body").addClass(theme);

if ($("body").hasClass("night")) {
  $(".dntoggle").addClass("fas fa-sun");
  $(".dntoggle").removeClass("fas fa-moon");
} else {
  $(".dntoggle").removeClass("fas fa-sun");
  $(".dntoggle").addClass("fas fa-moon");
}

$(".dntoggle").click(function () {
  $(".dntoggle").toggleClass("fas fa-sun");
  $(".dntoggle").toggleClass("fas fa-moon");

  if ($("body").hasClass("night")) {
    $("body").toggleClass("night");
    localStorage.removeItem("currentTheme");
    localStorage.currentTheme = "day";
  } else {
    $("body").toggleClass("night");
    localStorage.removeItem("currentTheme");
    localStorage.currentTheme = "night";
  }
});


function showTime(){
  var date = new Date();
  var h = date.getHours(); // 0 - 23
  var m = date.getMinutes(); // 0 - 59
  var s = date.getSeconds(); // 0 - 59
  var session = "AM";
  
  if(h == 0){
      h = 12;
  }
  
  if(h > 12){
      h = h - 12;
      session = "PM";
  }
  
  h = (h < 10) ? "0" + h : h;
  m = (m < 10) ? "0" + m : m;
  s = (s < 10) ? "0" + s : s;
  
  var time = h + ":" + m + ":" + s + " " + session;
  document.getElementById("MyClockDisplay").innerText = time;
  document.getElementById("MyClockDisplay").textContent = time;
  
  setTimeout(showTime, 1000);
  
}

showTime();