// goog.require('goog.dom');
// goog.require('goog.dom.classes');
// goog.require('portfolio.BigCardComponent');
// goog.require('portfolio.Helper');
// goog.require('portfolio.HomeCardComponent');
// goog.require('portfolio.ResumeCardComponent');

$(document).ready(function() {
  setChipContainerPosition();
  $(window).resize(setChipContainerPosition)
  const chips = $('.chip-wrapper').toArray();
  chips.forEach((chip) => {
    chip.onclick = (e) => {
      chips.forEach((chip) => {
        if (e.currentTarget == chip) {
          return;
        }
        $(chip).toggleClass('hidden');
      });
      $(e.currentTarget).toggleClass('expanded');
    };
  });
  $('.background')[0].onclick = (e) => {
    chips.forEach((chip) => {
      $(chip).removeClass('hidden');
      $(chip).removeClass('expanded');
    });
  };
});

function setChipContainerPosition() {
  $('.container-box')
      .css('margin-top', $('.info-header')[0].clientHeight + 36);
}
