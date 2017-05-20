$(function() {
  clickOnInputEntered();

  $('.submit').on('click', function(ev) {
    var username = $('#username').val();
    var password = $('#password').val();
    if (!validateUsernamePassword(username, password)) return;
    $.post('/login', {
      username: username,
      password: password
    }).done(function(res) {
      console.log(res);
      if (res.status == 'ok') {
        window.location.href = '/';
      } else if (res.status == 'error') {
        alert(res.detail);
      }
    });
  });
});
