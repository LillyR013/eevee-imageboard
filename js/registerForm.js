let form = document.getElementById("infoForm");
form.addEventListener("submit", function(e) {
    let passElem  = document.getElementsByName("password")[0];
    let pass = passElem.value;
    passElem.parentElement.removeChild(passElem);
    let hashHex = sha512(pass);
    document.getElementsByName("hashpass")[0].value = hashHex;
    return true;
})