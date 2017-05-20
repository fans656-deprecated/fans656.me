$(function() {
  clickOnInputEntered();

  $('.submit').on('click', function(ev) {
    var username = $('#username').val();
    var password = $('#password').val();
    var password2 = $('#password2').val();
    if (!validateUsernamePassword(username, password)) return;
    if (password !== password2) {
      alert('Passwords mismatch');
      $('#password2').focus();
      return;
    }
    $.post('/register', {
      username: username,
      password: password
    }).done(function(res) {
      console.log(res);
      if (res.status === 'error') {
        alert(res.detail);
      } else if (res.status === 'ok') {
        alert("Registration completed");
        window.location.href = "/login";
      }
    });
  });
});
