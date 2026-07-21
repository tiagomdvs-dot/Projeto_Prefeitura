document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('form-avaliacao');
    if (!form) return;

    var estrelas = form.querySelectorAll('.estrelas label');
    estrelas.forEach(function (label) {
        label.addEventListener('click', function () {
            estrelas.forEach(function (l) {
                l.style.transform = 'scale(1)';
            });
            this.style.transform = 'scale(1.3)';
        });
    });
});
