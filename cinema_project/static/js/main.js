// Валидация форм
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
});

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required]');

    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
            showError(input, getErrorMessage(input));
        } else {
            clearError(input);
        }
    });

    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const type = field.type;

    switch(type) {
        case 'email':
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        case 'text':
            if (field.name === 'full_name') {
                return /^[а-яА-ЯёЁ\s]+$/.test(value);
            }
            return value.length > 0;
        case 'password':
            if (field.name === 'password1') {
                return /^(?=.*[a-z])(?=.*[A-Z]).{6,}$/.test(value);
            }
            return true;
        default:
            return value.length > 0;
    }
}

function getErrorMessage(field) {
    const type = field.type;
    const name = field.name;

    if (field.name === 'full_name') {
        return 'ФИО должно содержать только кириллические символы';
    }
    if (field.name === 'email') {
        return 'Введите корректный email адрес';
    }
    if (field.name === 'password1') {
        return 'Пароль должен содержать минимум 6 символов, включая заглавные и строчные буквы';
    }
    return 'Это поле обязательно для заполнения';
}

function showError(field, message) {
    clearError(field);
    field.style.borderColor = '#ff2e63';
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.color = '#ff2e63';
    errorDiv.style.fontSize = '0.8rem';
    errorDiv.style.marginTop = '0.5rem';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearError(field) {
    field.style.borderColor = '';
    const errorDiv = field.parentNode.querySelector('.error-message');
    if (errorDiv) {
        errorDiv.remove();
    }
}