<?xml version="1.0"?>
<rss version="2.0">
 <channel><?cs
  if:project.name_encoded ?>
   <title><?cs var:project.name_encoded ?>: <?cs var:title ?></title><?cs
  else ?>
   <title><?cs var:title ?></title><?cs
  /if ?>
  <link><?cs var:base_host ?><?cs var:trac.href.blog ?></link>
  <description>Trac Blog</description>
  <language>en-us</language>
  <generator>Trac v<?cs var:trac.version ?></generator><?cs
  if:chrome.logo.src ?>
   <image>
    <title><?cs var:project.name_encoded ?></title>
    <url><?cs if:!chrome.logo.src_abs ?><?cs var:base_host ?><?cs /if ?><?cs
     var:chrome.logo.src ?></url>
    <link><?cs var:base_host ?><?cs var:trac.href.blog ?></link>
   </image><?cs
  /if ?><?cs
  each:event = blog.events ?>
   <item>
    <title><?cs var:event.title ?></title><?cs
    if:event.author.email ?>
     <author><?cs var:event.author.email ?></author><?cs
    /if ?>
    <pubDate><?cs var:event.rfcdate ?></pubDate>
    <link><?cs var:base_host ?><?cs var:event.href ?></link>
    <guid><?cs var:base_host ?><?cs var:event.href ?></guid>
    <description><?cs var:event.escaped ?></description>
   </item><?cs
  /each ?>
 </channel>
</rss>
