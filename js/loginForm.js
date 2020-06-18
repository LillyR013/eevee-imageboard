let form = document.getElementById("infoForm");
form.addEventListener("submit", function(e) {
    let passElem  = document.getElementsByName("password")[0];
    let pass = passElem.value;
    let nonceElem = document.getElementsByName("nonce")[0];
    let nonce = nonceElem.value;
    passElem.parentElement.removeChild(passElem);
    nonceElem.parentElement.removeChild(nonceElem);
    let cnonceArray = new Uint32Array(4);
    cnonceArray = crypto.getRandomValues(cnonceArray);
    let cnonceHexArray = [];
    for(let i=0; i<4; i++) {
        cnonceHexArray[i] = cnonceArray[i].toString(16);
    }
    let cnonce = cnonceHexArray.join("");
    document.getElementsByName("cnonce")[0].value = cnonce;
    let hashHex = sha512(pass+nonce+cnonce);
    document.getElementsByName("hashpass")[0].value = hashHex;
    return true;
})