$(document).ready(function () {
    function shuffleOptions() {
        let options = document.querySelectorAll('.form-check');
        for (let i = options.length - 1; i > 0; i--) {
            let j = Math.floor(Math.random() * (i + 1));
            options[i].parentNode.insertBefore(options[j], options[i].nextSibling);
            [options[i], options[j]] = [options[j], options[i]];
        }
    };shuffleOptions();
});