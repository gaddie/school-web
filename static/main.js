$(document).ready(function(){
  $(".header-right > a").click(function() {
    $(".hamburger-menu").addClass("active");

  });
  $(".close").click(function() {
    $(".hamburger-menu").removeClass("active");
    
  });
});