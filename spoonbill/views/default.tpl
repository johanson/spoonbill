<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{{file_name or 'Index'}} - Spoonbill</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{{site_url}}/static/normalize.css">
    <link rel="stylesheet" href="{{site_url}}/static/milligram.css">
    <link rel="stylesheet" href="{{site_url}}/static/style.css">
    <link rel="stylesheet" href="{{site_url}}/static/simplemde.min.css">
    <script src="{{site_url}}/static/simplemde.min.js" defer></script>
    <script src="{{site_url}}/static/main.js" defer></script>
</head>
<body>


<sidebar id="sidebar">
    <a href="#" id="menu">&nearr;</a>
    <input type="text" id="search" placeholder="Search">
    <ul id="list">
    % for i in file_list:
        <li><a href="{{site_url}}/edit/{{i}}">{{i}}</a></li>
    % end
   </ul>
   <a class="button" id="new_file" href="#">New file</a>
</sidebar>

<main id="main">
    <h2>{{file_name}}</h2>
    <form method="post" action="{{site_url}}/save/" accept-charset="utf-8">
        <textarea id="textarea" name="file_contents">{{file_contents}}</textarea>
        <input type="hidden" name="file_name" id="file_name" value="{{file_name or 'index'}}">
        <input type="submit" name="save" value="Save">
        <input type="submit" name="save_and_build" value="Save & Build">
        <input type="submit" name="delete_file" class="button-clear float-right" id="delete_file" value="Delete File">
    </form>
</main>

</body>
</html>