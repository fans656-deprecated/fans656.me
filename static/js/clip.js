var timeoutId;

$(function() {
  $('#clip').on('input propertychange change', function() {
    console.log('textarea change');
    clearTimeout(timeoutId);
    timeoutId = setTimeout(function() {
      fetch('/clip/save', {
        method: 'POST',
        credentials: 'include',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          data: $('#clip').val()
        })
      }).then(function(resp) {
        console.log(resp);
        console.log('saved at ' + new Date);
      });
    }, 1000);
  });
});
