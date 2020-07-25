function myFunction(sel) {
  var x = document.getElementById("mySelect").value;
    if(sel.val()!='Balcony') this.form.submit();
  document.getElementById("demo").innerHTML = "You selected: " + x;
}


$(document).ready(function(){
	$(window).scroll(function () {
			if ($(this).scrollTop() > 50) {
				$('#back-to-top').fadeIn();
			} else {
				$('#back-to-top').fadeOut();
			}
		});
		// scroll body to 0px on click
		$('#back-to-top').click(function () {
			$('body,html').animate({
				scrollTop: 0
			}, 800);
			return false;
		});
});