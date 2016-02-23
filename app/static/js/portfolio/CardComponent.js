goog.provide('portfolio.CardComponent');

goog.require('goog.ui.Component');

/**
 * A card
 *
 * @param {[type]} title         [description]
 * @param {Object} opt_domHelper [description]
 */
portfolio.CardComponent = function(title, opt_domHelper) {
  goog.base(this, opt_domHelper);
  this.title = title;
};
goog.inherits(portfolio.CardComponent, goog.ui.Component);
