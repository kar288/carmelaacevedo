// This file was automatically generated from simple.soy.
// Please don't edit this file by hand.

if (typeof portfolio == 'undefined') { var portfolio = {}; }


portfolio.homeCard = function(opt_data, opt_ignored) {
  var output = '<div class="chip-wrapper"><a class="chip-link" target="_top;" href="' + soy.$$escapeHtml(opt_data.url) + '"><div class="chip" hero-id="a" hero?="aa"><div class="chip-top ratio" style="background-image:url(\'' + soy.$$escapeHtml(opt_data.image) + '\');" hero-id="aa" hero?="aa"></div><div class="description">';
  var pList8 = opt_data.description;
  var pListLen8 = pList8.length;
  for (var pIndex8 = 0; pIndex8 < pListLen8; pIndex8++) {
    var pData8 = pList8[pIndex8];
    output += soy.$$escapeHtml(pData8) + '<br><br>';
  }
  output += '</div><div class="chip-bottom"><div class="chip-album-artist">' + soy.$$escapeHtml(opt_data.title) + '</div></div></div></a></div>';
  return output;
};


portfolio.resumeCard = function(opt_data, opt_ignored) {
  return '<div class="chip-wrapper"><div class="chip-container" hero-p on-tap="{{transition}}"><div class="chip" hero-id="' + soy.$$escapeHtml(opt_data.title) + '" hero?="{{selectedCard === item}}"><div class="chip-top" style="background:' + soy.$$escapeHtml(opt_data.color) + ';" hero-id="' + soy.$$escapeHtml(opt_data.title) + '" hero?="{{selectedCard === item}}"></div><div class="chip-bottom"><div class="chip-album-artist">' + soy.$$escapeHtml(opt_data.title) + '</div></div></div></div></div>';
};


portfolio.bigCard = function(opt_data, opt_ignored) {
  var output = '<div class="card row" layout horizontal hero-id="' + soy.$$escapeHtml(opt_data.title) + '-art" hero on-tap="{{transition}}"><div class="card-left col-lg-4" style="background:' + soy.$$escapeHtml(opt_data.color) + ';" hero-id="' + soy.$$escapeHtml(opt_data.title) + '-art" hero></div><div class="card-right col-lg-8" flex><div layout horizontal center><div><div class="card-icon" style="background:' + soy.$$escapeHtml(opt_data.color) + ';"></div></div><div flex><div class="card-title">' + soy.$$escapeHtml(opt_data.title) + '</div></div></div><div class="elements" center>';
  var elementList37 = opt_data.elements;
  var elementListLen37 = elementList37.length;
  for (var elementIndex37 = 0; elementIndex37 < elementListLen37; elementIndex37++) {
    var elementData37 = elementList37[elementIndex37];
    output += '<div><div class="row"><div class="col-xs-8 title"><h5>' + soy.$$escapeHtml(elementData37.main) + '</h5></div><div class="col-xs-4 date">' + soy.$$escapeHtml(elementData37.date) + '</div></div>' + ((elementData37.place) ? '<div class="place">' + soy.$$escapeHtml(elementData37.place) + '</div>' : '') + '<div>' + soy.$$escapeHtml(elementData37.description) + '</div><div>' + soy.$$escapeHtml(elementData37.description2) + '</div></div><hr>';
  }
  output += '</div></div></div>';
  return output;
};
