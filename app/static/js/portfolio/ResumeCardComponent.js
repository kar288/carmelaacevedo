goog.provide('portfolio.ResumeCardComponent');

// goog.require('goog.events.EventTarget');
// goog.require('goog.events.EventType');
goog.require('portfolio.CardComponent');

/**
 * [CardComponent description]
 * @param {[type]} title         [description]
 * @param {[type]} url           [description]
 * @param {[type]} image         [description]
 * @param {[type]} description   [description]
 * @param {[type]} opt_domHelper [description]
 */
portfolio.ResumeCardComponent =
  function(title, color, detailWindow, opt_domHelper) {
    goog.base(this, title, opt_domHelper);
    this.color = color;
    this.detailWindow = detailWindow;
};
goog.inherits(portfolio.ResumeCardComponent, portfolio.CardComponent);

/**
 * [createDom description]
 */
portfolio.ResumeCardComponent.prototype.createDom = function() {
  var data = {
    title: this.title,
    color: this.color
  };
  var template = portfolio.resumeCard(data);
  var element = this.dom_.htmlToDocumentFragment(template);
  this.decorateInternal(element);
};

/**
 * [enterDocument description]
 */
// portfolio.ResumeCardComponent.prototype.enterDocument = function() {
//   goog.base(this, 'enterDocument');
//   // this.getHandler().listen(this.getContentElement(),
//   //   goog.events.EventType.MOUSEENTER,
//   //   function(e) {
//   //     goog.dom.classes.add(this.getElement(), 'onHover');
//   //   });
//   // this.getHandler().listen(this.getContentElement(),
//   //   goog.events.EventType.MOUSELEAVE,
//   //   function(e) {
//   //     goog.dom.classes.remove(this.getElement(), 'onHover');
//   //   });
// };
