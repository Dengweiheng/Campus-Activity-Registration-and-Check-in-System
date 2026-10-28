// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        document.querySelectorAll('.alert').forEach(function (el) {
            el.style.transition = 'opacity .5s';
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 500);
        });
    }, 5000);

    // Animate stat numbers
    document.querySelectorAll('.stat-card-num[data-target]').forEach(function (el) {
        var target = parseInt(el.dataset.target, 10);
        var current = 0;
        var step = Math.ceil(target / 40);
        var timer = setInterval(function () {
            current = Math.min(current + step, target);
            el.textContent = current;
            if (current >= target) clearInterval(timer);
        }, 30);
    });
});
