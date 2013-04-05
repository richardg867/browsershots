function select_browsers(selection) {
  for (s=0; s<=selection.length; s++) {
    if (selection.charAt(s)=='+')
      document.forms['startform'].elements[s+2].checked='checked';
    if (selection.charAt(s)=='-')
      document.forms['startform'].elements[s+2].checked='';
  }
}
