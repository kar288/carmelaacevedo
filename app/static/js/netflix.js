var moviesRow = $('.movies-row');
var pathname = document.location.pathname.split('/');
$.get('/getMovies/' + pathname[pathname.length - 1], function(data) {
  $('.list-title').append($.parseHTML('<div>' + data.title + '</div>'));
  if (data.description) {
    $('.list-description').append(
      $.parseHTML('<div>' + data.description + '</div>')
    );
  }
  data.movies.forEach(function(movie) {
    $.get('/getMovie/' + movie.year + '/' + movie.title , function(data) {
      moviesRow.append($.parseHTML(data));
    });
  });
});
