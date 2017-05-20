var timeoutId;

$(function() {
  $('#clip').on('input propertychange change', function() {
    console.log('textarea change');
    clearTimeout(timeoutId);
    timeoutId = setTimeout(function() {
      $.post('/clip/save', {
        data: $('#clip').val()
      }).done(function() {
        console.log('saved');
      });
    }, 1000);
  });
});
