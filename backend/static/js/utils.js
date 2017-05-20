function clickOnInputEntered() {
  $('input[type="text"], input[type="password"]').on('keyup', function(ev) {
    if (ev.keyCode == 13) {
      $('.submit').click();
    }
  });
}

function validateUsernamePassword(username, password) {
  if (!username) {
    alert('Username can not be empty');
    $('#username').focus();
    return false;
  }
  if (!password) {
    alert('Password can not be empty');
    $('#password').focus();
    return false;
  }
  if (username.length > 255) {
    alert('Username is too long');
    return false;
  }
  if (password.length > 255) {
    alert('Password is too long');
    return false;
  }
  return true;
}
