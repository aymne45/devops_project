// Système de notifications toast et modals pour l'application ENT

// Initialiser le container de toasts au chargement
document.addEventListener('DOMContentLoaded', () => {
    if (!document.getElementById('toast-container')) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
});

// Système de notifications toast
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>',
        error: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>',
        info: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
        warning: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>'
    };
    
    toast.innerHTML = `
        <div class="flex-shrink-0">${icons[type]}</div>
        <div class="flex-1 font-medium">${message}</div>
        <button onclick="this.parentElement.remove()" class="flex-shrink-0 opacity-70 hover:opacity-100">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Modal de confirmation
function showConfirm(message, onConfirm, confirmText = 'Confirmer', type = 'primary') {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const colors = {
        primary: 'bg-teal-600 hover:bg-teal-700',
        danger: 'bg-red-600 hover:bg-red-700'
    };
    
    overlay.innerHTML = `
        <div class="modal-content">
            <h3 class="text-lg font-bold text-gray-800 mb-4">Confirmation</h3>
            <p class="text-gray-600 mb-6">${message}</p>
            <div class="flex gap-3 justify-end">
                <button onclick="this.closest('.modal-overlay').remove()" 
                        class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg font-medium transition">
                    Annuler
                </button>
                <button id="confirm-btn" 
                        class="px-4 py-2 ${colors[type]} text-white rounded-lg font-medium transition">
                    ${confirmText}
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    document.getElementById('confirm-btn').onclick = () => {
        overlay.remove();
        onConfirm();
    };
    
    overlay.onclick = (e) => {
        if (e.target === overlay) overlay.remove();
    };
}

// Styles CSS à injecter
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    /* Toast notifications */
    .toast-container { position: fixed; top: 20px; right: 20px; z-index: 9999; }
    .toast { min-width: 300px; padding: 16px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.15); 
             display: flex; align-items: center; gap: 12px; margin-bottom: 12px;
             animation: slideIn 0.3s ease-out; }
    .toast.success { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; }
    .toast.error { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; }
    .toast.info { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; }
    .toast.warning { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; }
    @keyframes slideIn { from { transform: translateX(400px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(400px); opacity: 0; } }
    .toast.hiding { animation: slideOut 0.3s ease-in; }
    
    /* Modal de confirmation */
    .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 9998; 
                     display: flex; align-items: center; justify-content: center; animation: fadeIn 0.2s; }
    .modal-content { background: white; border-radius: 16px; padding: 24px; max-width: 400px; width: 90%; 
                    box-shadow: 0 20px 50px rgba(0,0,0,0.3); animation: scaleIn 0.2s; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes scaleIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
`;
document.head.appendChild(notificationStyles);
