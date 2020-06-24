var btnList = document.getElementsByTagName("button");
for(var i=0; i<btnList.length; i++) {
    var btn = btnList[i];
    btn.addEventListener("click", function() {
        id = btn.name.substring(6);
        document.getElementsByName("tagID")[0].value = id;
        document.getElementsByTagName("form")[0].submit();
    });
}