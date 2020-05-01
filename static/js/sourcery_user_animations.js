// Copyright (c) 2020 Roberto Treviño Cervantes

// This file is part of FUTURE (Powered by Monad).

// FUTURE is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// FUTURE is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with FUTURE.  If not, see <https://www.gnu.org/licenses/>.

// ALLOW TO UPLOAD FILES
var file_inputs = document.querySelectorAll( '.file_inputs' );
Array.prototype.forEach.call( file_inputs, function( file_input ) {
  var label	= file_input.nextElementSibling,
      labelVal = label.innerHTML;
  file_input.addEventListener( 'change', function( e ) {
      var fileName = '';
      if( this.files && this.files.length > 1 ) {
        label.innerHTML = (this.getAttribute( 'data-multiple-caption' ) || '' ).replace( '{count}', this.files.length);
      } else {
        label.innerHTML = e.target.value.split( '\\' ).pop();
      }
  });
});

// TODO: GET HEIGHT TO LOAD POSTS WITH AJAX
// function getDocHeight() {
//     var D = document;
//     return Math.max(
//         D.body.scrollHeight, D.documentElement.scrollHeight,
//         D.body.offsetHeight, D.documentElement.offsetHeight,
//         D.body.clientHeight, D.documentElement.clientHeight
//     );
// }

$(function() {
  // SEND MAIN FORM WITH AJAX
  var submit_form = function(e) {
    e.preventDefault();
    data = new FormData($("#publication_form")[0])

    $.ajax({
      url: $SCRIPT_ROOT + '/_upload/' + $USERNAME,
      type: 'POST',
      data: data,
      processData: false,
      contentType: false
    })

  };

  $("#publication_form").submit(function(e) {
    submit_form();
  });

  $('#writebutton').bind('click', submit_form);
  $('#publication').bind('keydown', function(e) {
    if (e.keyCode == 13) {
      submit_form();
    }
  });

  // SEND SECOND FORM WITH AJAX
  var submit_form2 = function(e) {
    e.preventDefault();
    data = new FormData($("#publication_form2")[0])

    $.ajax({
      url: $SCRIPT_ROOT + '/_upload',
      type: 'POST',
      data: data,
      processData: false,
      contentType: false
    })

  };

  $("#publication_form2").submit(function(e) {
    submit_form2();
  });

  $('#writebutton2').bind('click', submit_form2);
  $('#publication2').bind('keydown', function(e) {
    if (e.keyCode == 13) {
      submit_form2();
    }
  });

  // // TODO: SHOW RESULTS WITH AJAX
  // $(window).scroll(function() {
  //      if($(window).scrollTop() + $(window).height() == getDocHeight()) {
  //        get_posts()
  //      }
  //  });
});
