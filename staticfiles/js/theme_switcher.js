// static/js/theme_switcher.js

document.addEventListener('DOMContentLoaded', function() {
    const htmlElement = document.documentElement;
    const themeCookieName = 'D-Stroy_theme';

    // 1. Функция для установки темы и куки
    function setTheme(theme) {
        // Установка атрибута data-bs-theme для Bootstrap
        htmlElement.setAttribute('data-bs-theme', theme);
        
        // Установка куки (для сохранения выбора между сессиями)
        document.cookie = `${themeCookieName}=${theme}; path=/; max-age=31536000; secure`; 
        
        // Обновление темы на навигационной панели
        const navbar = document.getElementById('mainNavbar');
        if (navbar) {
             navbar.setAttribute('data-bs-theme', theme);
        }
    }

    // 2. Функция для получения куки
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    // 3. Применение темы при загрузке страницы
    function applyInitialTheme() {
        const savedTheme = getCookie(themeCookieName);
        
        // A. Если есть куки, используем его (приоритет)
        if (savedTheme) {
            setTheme(savedTheme);
            return; 
        }

        // B. Если куки нет, пытаемся получить тему из сессии Django (передана из Base.html)
        // Нам нужно прочитать тему, которую Django записал в сессию после входа.
        // Для этого мы будем использовать скрытый элемент (см. ниже Шаг 3).
        const djangoThemeElement = document.getElementById('django-initial-theme');
        if (djangoThemeElement && djangoThemeElement.dataset.theme) {
            const initialTheme = djangoThemeElement.dataset.theme;
            setTheme(initialTheme);
        }
        
        // Если ничего нет, остаётся light (тема по умолчанию)
    }

    // 4. Мгновенное переключение темы на странице профиля
    const themeSelector = document.getElementById('id_theme');
    if (themeSelector) {
        themeSelector.addEventListener('change', function() {
            const newTheme = this.value;
            setTheme(newTheme);
            // При отправке формы Django сохранит это значение в БД
        });
    }
    
    // Вызов функции при загрузке
    applyInitialTheme();
});