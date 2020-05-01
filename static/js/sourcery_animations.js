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

function getDocHeight() {
    var D = document;
    return Math.max(
        D.body.scrollHeight, D.documentElement.scrollHeight,
        D.body.offsetHeight, D.documentElement.offsetHeight,
        D.body.clientHeight, D.documentElement.clientHeight
    );
}

// LOAD POSTS WITH AJAX
function get_posts() {
  $.getJSON($SCRIPT_ROOT + '/_posts', {}, function(data) {
      data.result.forEach(function(post) {
          $('#user_list').append('<div class="user_item"><p><a href="/iw/user/' + post[0] + '" style="color: #d4a45d">' + post[0] + '</a> <span style="color: #DDDDDD">' + post[2] + ':</span></p><p>' + post[1] + '<p></div><br>')
      });
  });
}

// ALLOW TO SEND FILES
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

$(function() {
  // SEND FORM WITH AJAX
  var submit_form = function(e) {
    e.preventDefault();
    data = new FormData($("#publication_form")[0])

    $.ajax({
      url: $SCRIPT_ROOT + '/_upload',
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

  // LOAD INITIAL POSTS WITH AJAX
  get_posts()

  // AS THE USER SCROLLS, LOAD MORE POSTS WITH AJAX
  $(window).scroll(function() {
       if($(window).scrollTop() + $(window).height() == getDocHeight()) {
         get_posts()
       }
   });
});
