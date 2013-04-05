<?cs include "header.cs"?>

<div id="ctxtnav" class="nav"></div>

<div id="content" class="wikipage">
<?cs
each:event = blog.events ?>
<h1><a href="<?cs var:event.href ?>" style="border-bottom-style: none; color: black;"><?cs var:event.title ?></a></h1>
<p style="font-size: smaller; color: gray; margin: 0 0 0 -18px;"><?cs var:event.date ?> | <?cs var:event.author ?> | <a href="<?cs var:event.href ?>" title="permalink" style="border-bottom-style: none;">#</a><?cs
if:event.comments ?> | <?cs var:event.comments ?> comments<?cs /if ?>
<?cs var:event.description ?>
<?cs /each ?>

<div id="help">
 <hr />
 <strong>Note:</strong> See <a href="<?cs var:trac.href.wiki ?>/SimpleBlogPlugin">SimpleBlogPlugin</a>
 for information about the blog view.
</div>

</div>

<?cs include "footer.cs"?>
