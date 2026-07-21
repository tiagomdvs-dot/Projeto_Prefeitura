document.addEventListener('DOMContentLoaded', function () {
    var fotoInput = document.getElementById('foto');
    var fotoLabel = document.querySelector('.btn-foto');

    if (fotoInput && fotoLabel) {
        fotoInput.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                fotoLabel.textContent = '\uD83D\uDCF7 ' + this.files[0].name;
            } else {
                fotoLabel.innerHTML = '\uD83D\uDCF7 Anexar foto';
            }
        });
    }
});
