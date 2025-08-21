window.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.field-status').forEach((el) => {
        if (el.querySelector('select')) return;
        const status = el.textContent;
        const statusEl = document.createElement('span');
        statusEl.textContent = status;
        statusEl.style.padding = '0 5px 2px 5px'
        statusEl.style.borderRadius = '5px';
        statusEl.classList.add('text-nowrap');
        el.innerHTML = '';
        console.log(status)
        if (status === 'Отправлено'
        ) {
            statusEl.style.backgroundColor = '#46a350'
        } else if (status.includes('Ошибка')) {
            statusEl.style.backgroundColor = '#ce3244'
        } else if (status.includes('В ожидании')) {
            statusEl.style.backgroundColor = '#3276ce'
        }
        el.appendChild(statusEl);
    });
})
// '#59ff69'
// '#ff324b'
// '#3089ff'
