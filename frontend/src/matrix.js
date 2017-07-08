import $ from 'jquery'

let timer = null;
let timerOverlay = null;

export default function installMatrix() {
  const overlay = $('<div id="matrix-effect-overlay">');
  const canvas = $('<canvas id="matrix-effect-canvas">');

  $(document).keypress(onKeypress);

  canvas.attr('width', window.innerWidth);
  canvas.attr('height', window.innerHeight);
  canvas.click(removeSelf);

  $('body').append(overlay).append(canvas);
  overlay.css({
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    background: 'black',
    opacity: 0,
  });
  canvas.css({
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    opacity: 1,
  });

  overlay.animate({opacity: 0.9}, 1500);
  overlay.animate({opacity: 0.985}, 3000);


  // source code from
  // http://fans656.html-5.me/
  //
  // setup
  var width = $('body').width();
  var height = $('body').height();
  var ctx = $('#matrix-effect-canvas').attr({width: width, height: height})[0].getContext('2d');
  // set ctx
  ctx.font = 'bold ' + cellHeight + 'px "matrix"';
  ctx.textBaseline = 'top';
  ctx.textAlign = 'left';
  //
  maxRow = Math.floor(height / cellHeight);
  maxCol = Math.floor(width / cellWidth);
  // background matrix
  var bg = new Array(maxRow);
  var chars = 'abcdefghijklmnopqrstuvwxyz0123456789$+-*/=%"\'#&_(),.;:?!\\|{}<>[]^~';
  var n = chars.length - 1;
  function randchar() {
    return chars[randint(0, n)];
  }
  for (var i = 0; i <= maxRow; ++i) {
    bg[i] = new Array(maxCol);
    for (var j = 0; j <= maxCol; ++j) {
      bg[i][j] = randchar();
    }
  }
  // worms
  var worms = new Array(10);
  worms.max = maxCol * 2;
  for (var i = 0; i < worms.length; ++i) {
    worms[i] = new Worm();
  }
  // worm increment
  function addWorm() {
    if (worms.length < worms.max) {
      worms.push(new Worm());
      setTimeout(addWorm, 200);
    }
  }
  setTimeout(addWorm, 2000);
  // animation interval
  setInterval(function() {
    ctx.clearRect(0, 0, width, height);
    for (var i = 0; i < worms.length; ++i) {
      worms[i].go();
      if (worms[i].dead()) {
        worms[i] = new Worm();
      }
      draw(worms[i]);
    }
  }, 100);
  
  function draw(w) {
    var tail = w.row - w.length;
    var head = w.row;
    var beg = Math.max(0, tail);
    var end = Math.min(maxRow, head);
    var col = w.col;
    
    ctx.fillStyle = '#04B404';
    for (var i = beg; i < end; ++i) {
      ctx.fillText(bg[i][col], cellWidth * col, cellHeight * i);
    }
    if (0 <= tail) {
      ctx.fillStyle = '#0B3B0B';
      ctx.fillText(bg[tail][col], cellWidth * col, cellHeight * tail);
    }
    if (i == head) {
      ctx.fillStyle = '#40FF00';
      ctx.fillText(bg[i][col], cellWidth * col, cellHeight * i);
    }
  }
}

function removeSelf() {
  $('#matrix-effect-canvas').remove();
  $('#matrix-effect-overlay').remove();
  if (timer) {
    clearInterval(timer);
  }
  $(document).unbind('keypress', onKeypress);
}

function onKeypress(ev) {
  ev.preventDefault();
  removeSelf();
}

var cellWidth = 20, cellHeight = 15;
var min = 2, max = 20;
var maxRow, maxCol;
var bg = [];
// Worm
function Worm() {
  this.length = randint(min, max);
  this.row = randint(-max, 0);
  this.col = randint(0, maxCol);
}
Worm.prototype.go = function() {
  ++this.row;
};
Worm.prototype.dead = function() {
  return this.row - this.length > maxRow;
};
// utils
function randint(lo, hi) {
  return lo + Math.floor(lo + (hi - lo + 1) * Math.random());
}
