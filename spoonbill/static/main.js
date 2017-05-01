(function() {

    // Init simplemde
    var simplemde = new SimpleMDE({ 
        element: document.getElementById('textarea'),
        spellChecker: false,
    });

    // Toggle menu for small viewports
    var menu = document.getElementById('menu');
    var sidebar = document.getElementById('sidebar');
    menu.onclick = function(e) {
        e.preventDefault();
        sidebar.classList.toggle('toggle');
    }

    // Create new file
    var new_file = document.getElementById('new_file')
    new_file.onclick = function(e) {
        e.preventDefault();
        var new_file_name = prompt("Enter the file name", "my-file.md");
        if (new_file_name != null) {
            window.location.href = "/edit/" + new_file_name;
        }
    }

    // Delete file
    var delete_file = document.getElementById('delete_file');
    delete_file.onclick = function(e) {
        e.preventDefault();
        var file_name = document.getElementById('file_name').value;
        if (window.confirm("Are you sure you want to delete " +
                           "the file " + file_name + "?")) {
            window.location.href = "/delete/" + file_name;
        }
    }

    // Search onkeyup handler
    var search = document.getElementById('search')
    search.onkeyup = function(e) {
        filter_search()
    }

})();

// Filter serach results
function filter_search() {
    var search_text = document.getElementById('search').value.toUpperCase();
    var list = document.querySelectorAll('#list li');
    for (var i = 0; list[i]; i++) {
        if (list[i].textContent.toUpperCase().indexOf(search_text) > -1) {
            list[i].style.display = "";
        } else {
            list[i].style.display = "none";
        }
    }
}
