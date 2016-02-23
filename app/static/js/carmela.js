// goog.require('goog.dom');
// goog.require('goog.dom.classes');
// goog.require('portfolio.BigCardComponent');
// goog.require('portfolio.Helper');
// goog.require('portfolio.HomeCardComponent');
// goog.require('portfolio.ResumeCardComponent');

$(document).ready(function() {
  var resumeContent = $('.resume-content')[0];
  if (resumeContent) {
    var resumeImage = $('.resume-image')[0];
    resumeContent.style.marginLeft = resumeImage.width;
    resumeContent.style.maxWidth = $(window).width() - resumeImage.width;
  }

  var chipContainerHome = $('.chip-container-home')[0];
  var chipContainerResume = $('.chip-container-resume')[0];
  if (chipContainerResume) {
    // renderResumeCards();
  }
});

function renderResumeCards() {
  var cards = [];
  cards.push(new portfolio.ResumeCardComponent(
    'Education',
    '#333'));
  cards.push(new portfolio.ResumeCardComponent(
    'Skills',
    '#555'));
  cards.push(new portfolio.ResumeCardComponent(
    'Honours and Awards',
    '#777'));
  cards.push(new portfolio.ResumeCardComponent(
    'Professional Experience',
    '#999'));
  cards.push(new portfolio.ResumeCardComponent(
    'Publications',
    '#BBB'));
  for (var i = 0; i < cards.length; i++) {
    cards[i].render($('.chip-container-resume')[0]);
  }
}
