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

    var tipoSelect = document.getElementById('tipo');
    var setorInfo = document.getElementById('setor-info');
    var setorNome = document.getElementById('setor-nome');

    if (tipoSelect && setorInfo && setorNome) {
        tipoSelect.addEventListener('change', function () {
            var tipo = this.value;
            if (tipo && window.TIPO_SETOR_MAP && window.TIPO_SETOR_MAP[tipo]) {
                setorNome.textContent = window.TIPO_SETOR_MAP[tipo];
                setorInfo.style.display = 'flex';
            } else {
                setorInfo.style.display = 'none';
            }
        });
    }
});
