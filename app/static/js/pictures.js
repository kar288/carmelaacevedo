$(document).ready(function() {
  var largeImage = $('.large-image');

  $('.mover.right').on('click', function() {
    passPicture(1);
  });

  $('.mover.left').on('click', function() {
    passPicture(-1);
  });

  largeImage.on('click', function() {
    passPicture(1);
  });

  $('.small-picture[index="0"').addClass('selected');
  $('.small-picture').on('click', function() {
    var el = $(this);
    var index = el.attr('index') * 1;
    setPictureIndex(largeImage, index + 2);
  });
});

var passPicture = function(direction) {
  var largeImage = $('.large-image');
  var index = parseInt(largeImage.attr('index'));
  index += direction;
  setPictureIndex(largeImage, index);
};

var setPictureIndex = function(image, index) {
  if (index < 2) {
    index = 15;
  } else if (index > 15) {
    index = 2;
  }
  image.attr('src', '/static/images/mutableLandscapes' + index + '.png');
  image.attr('index', index);
  $('.small-picture').removeClass('selected');
  $('.small-picture[index="' + index + '"').addClass('selected');
};
