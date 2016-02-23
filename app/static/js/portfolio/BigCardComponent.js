goog.provide('portfolio.BigCardComponent');

goog.require('portfolio.CardComponent');

/**
 * [CardComponent description]
 * @param {[type]} title         [description]
 * @param {[type]} url           [description]
 * @param {[type]} image         [description]
 * @param {[type]} description   [description]
 * @param {[type]} opt_domHelper [description]
 */
portfolio.BigCardComponent = function(title, color, elements, opt_domHelper) {
  goog.base(this, title, opt_domHelper);
  this.color = color;
  this.elements = elements;
};

goog.inherits(portfolio.BigCardComponent, portfolio.CardComponent);

/**
 * [createDom description]
 */
portfolio.BigCardComponent.prototype.createDom = function() {
  var data = {
    title: this.title,
    color: this.color,
    elements: this.elements
  };
  var template = portfolio.polymerStuff();
  var element = this.dom_.htmlToDocumentFragment(template);
  this.decorateInternal(element);
};
