document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('form-cadastro');
    if (!form) return;

    var cpfInput = document.getElementById('cpf');
    var senhaInput = document.getElementById('senha');
    var confirmarInput = document.getElementById('confirmar_senha');

    cpfInput.addEventListener('input', function () {
        var value = this.value.replace(/\D/g, '');
        if (value.length <= 3) {
            this.value = value;
        } else if (value.length <= 6) {
            this.value = value.slice(0, 3) + '.' + value.slice(3);
        } else if (value.length <= 9) {
            this.value = value.slice(0, 3) + '.' + value.slice(3, 6) + '.' + value.slice(6);
        } else {
            this.value = value.slice(0, 3) + '.' + value.slice(3, 6) + '.' + value.slice(6, 9) + '-' + value.slice(9, 11);
        }
    });

    form.addEventListener('submit', function (e) {
        var senha = document.getElementById('senha').value;
        var confirmar = document.getElementById('confirmar_senha').value;

        if (senha.length < 6) {
            e.preventDefault();
            alert('A senha deve ter no mínimo 6 caracteres.');
            return;
        }

        if (senha !== confirmar) {
            e.preventDefault();
            alert('As senhas não conferem.');
            return;
        }
    });
});
