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

// SWITCH TO DIFFERENT LAYOUT DUE TO SCREEN SIZE
if ($(window).height() <= 768 && $(window).width() <= 960) {
    $('.file_inputs')[0].remove()
}

// CODE FOR MULTIPLE FILE CAPTION
var file_inputs = document.querySelectorAll('.file_inputs');
Array.prototype.forEach.call(file_inputs, function(file_input) {
    var label = file_input.nextElementSibling,
        labelVal = label.innerHTML;
    file_input.addEventListener('change', function(e) {
        var fileName = '';
        if (this.files && this.files.length > 1) {
            label.innerHTML = (this.getAttribute('data-multiple-caption') || '').replace('{count}', this.files.length);
        } else {
            label.innerHTML = e.target.value.split('\\').pop();
        }
    });
});

// CODE FOR FILE SEARCH ENGINE
function search_file(q) {
    $.getJSON($SCRIPT_ROOT + '/_files', {
        q: q
    }, function(data) {
        data.result.forEach(function(file) {
            grid.append('<div class="grid-item"><div class="file_options"><i class="ion-document"></i> - <a href="/MAZE/' + file + '"><i class="ion-arrow-down-c"></i></a> <a href="/edit/' + file + '"><i class="ion-edit"></i></a> <a href="/remove/' + file + '"><i class="ion-backspace"></i></a>  <a onclick="openshare(' + file + ')" href="#openShare"><i class="ion-share"></i></a></div><div class="file_name"><a href="/MAZE/' + file + '">' + file + '</a></div></div>')
        });
    });
}

// INITIALLY SHOW ALL FILES
search_file("")

// AS INPUT CONTENT CHANGES, SHOW RELEVANT FILES
var search_input = $('#searchbar'),
    grid = $('#grid')

search_input.on('input', function(e) {
    grid.html("")
    search_file(search_input.val())
});