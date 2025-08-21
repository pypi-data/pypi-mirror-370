$(document).ready(function() {
    console.log('Simple sidebar script loaded');
    
    // Проверяем настройки Jazzmin
    console.log('Body classes:', document.body.className);
    console.log('Show sidebar setting:', document.body.classList.contains('sidebar-mini'));
    
    const toggle = document.getElementById('sidebarToggle');
    console.log('Toggle element:', toggle);
    
    const sidebar = document.getElementById('jazzy-sidebar');
    console.log('Sidebar element:', sidebar);
    
    const overlay = document.getElementById('sidebar-overlay');
    console.log('Overlay element:', overlay);
    
    const closeBtn = document.getElementById('sidebarCloseBtn');
    console.log('Close button element:', closeBtn);
    
    const body = document.body;
    
    // Проверяем все элементы с похожими ID
    console.log('All elements with "sidebar" in ID:', document.querySelectorAll('[id*="sidebar"]'));
    console.log('All elements with "jazzy" in ID:', document.querySelectorAll('[id*="jazzy"]'));
    
    // Проверяем начальное состояние sidebar
    if (sidebar) {
        console.log('Initial sidebar transform:', sidebar.style.transform);
        console.log('Initial sidebar display:', window.getComputedStyle(sidebar).display);
        console.log('Initial sidebar visibility:', window.getComputedStyle(sidebar).visibility);
        console.log('Initial sidebar z-index:', window.getComputedStyle(sidebar).zIndex);
        console.log('Initial sidebar position:', window.getComputedStyle(sidebar).position);
        console.log('Initial sidebar left:', window.getComputedStyle(sidebar).left);
        console.log('Initial sidebar width:', window.getComputedStyle(sidebar).width);
        console.log('Initial sidebar height:', window.getComputedStyle(sidebar).height);
    }
    
    if (toggle) {
        const closeSidebar = () => {
            body.classList.remove('sidebar-open');
            console.log('Sidebar closed');
        };
        
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            body.classList.toggle('sidebar-open');
            console.log('!!!!!!!! Sidebar toggled, body classes:', body.className);
            
            if (sidebar) {
                console.log('Sidebar transform after toggle:', sidebar.style.transform);
                console.log('Sidebar computed transform:', window.getComputedStyle(sidebar).transform);
                console.log('Sidebar display after toggle:', window.getComputedStyle(sidebar).display);
                console.log('Sidebar visibility after toggle:', window.getComputedStyle(sidebar).visibility);
                console.log('Sidebar z-index after toggle:', window.getComputedStyle(sidebar).zIndex);
                console.log('Sidebar position after toggle:', window.getComputedStyle(sidebar).position);
                console.log('Sidebar left after toggle:', window.getComputedStyle(sidebar).left);
                console.log('Sidebar width after toggle:', window.getComputedStyle(sidebar).width);
            }
            
            // Проверяем содержимое sidebar
            const sidebarContent = sidebar ? sidebar.querySelector('.sidebar') : null;
            if (sidebarContent) {
                console.log('Sidebar content found:', sidebarContent);
                console.log('Sidebar content HTML:', sidebarContent.innerHTML.substring(0, 200) + '...');
            } else {
                console.log('No sidebar content found');
            }
            
            // Проверяем overlay
            if (overlay) {
                console.log('Overlay opacity after toggle:', window.getComputedStyle(overlay).opacity);
                console.log('Overlay visibility after toggle:', window.getComputedStyle(overlay).visibility);
            }
        });
        
        // Обработчик для кнопки закрытия
        if (closeBtn) {
            closeBtn.addEventListener('click', closeSidebar);
        }
        
        // Обработчик для клика вне sidebar
        if (overlay) {
            overlay.addEventListener('click', closeSidebar);
        }
        
        // Обработчик клавиши Escape
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && body.classList.contains('sidebar-open')) {
                closeSidebar();
            }
        });
    } else {
        console.error('Sidebar toggle button not found!');
        console.log('Available buttons:', document.querySelectorAll('button'));
        console.log('Elements with sidebarToggle ID:', document.querySelectorAll('#sidebarToggle'));
        console.log('All nav-link elements:', document.querySelectorAll('.nav-link'));
    }
});