// Fichier JavaScript principal pour le Système d'Alerte Précoce IA Multi-Maladies

document.addEventListener('DOMContentLoaded', function() {
    // Fermer automatiquement les alertes après 5 secondes
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Activer les infobulles partout
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Activer les popovers partout
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Validation de formulaire
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Gestionnaire de sélection de menu déroulant
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    dropdownItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('data-target');
            const value = this.getAttribute('data-value');
            const text = this.textContent;
            
            if (target) {
                document.getElementById(target).value = value;
                document.querySelector(`[data-bs-target="#${target}"]`).textContent = text;
            }
        });
    });

    // Gérer la sélection de maladie dans le formulaire de prédiction
    const diseaseSelect = document.getElementById('disease');
    if (diseaseSelect) {
        diseaseSelect.addEventListener('change', function() {
            // Ceci est géré dans le modèle predict.html
        });
    }

    // Récupérer les données API pour le tableau de bord si sur la page du tableau de bord
    const dashboardCharts = document.getElementById('riskDistributionChart');
    if (dashboardCharts) {
        // Ceci est géré dans le modèle dashboard.html
    }
});
