document.addEventListener('DOMContentLoaded', () => {
    const messageContainer = document.getElementById('messageContainer');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const themeToggle = document.getElementById('themeToggle');
    const suggestionChips = document.querySelectorAll('.chip');

    // Vérifier la préférence de thème
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    const currentTheme = localStorage.getItem('theme');
    
    if (currentTheme === 'dark' || (!currentTheme && prefersDarkScheme.matches)) {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
    }

    // Toggle thème clair/sombre
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        // Animation de transition
        document.documentElement.classList.add('theme-transition');
        
        setTimeout(() => {
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            setTimeout(() => {
                document.documentElement.classList.remove('theme-transition');
            }, 300);
        }, 50);
    });

    // Auto-resize textarea avec animation fluide
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 200) + 'px';
    });

    // Activer l'envoi avec Entrée (Shift+Entrée pour nouvelle ligne)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendBtn.click();
        }
    });

    // Animation du bouton d'envoi
    sendBtn.addEventListener('mousedown', function() {
        const ripple = this.querySelector('.send-ripple');
        ripple.style.opacity = '1';
        ripple.style.transform = 'scale(0)';
        
        setTimeout(() => {
            ripple.style.transform = 'scale(4)';
            setTimeout(() => {
                ripple.style.opacity = '0';
            }, 300);
        }, 10);
    });

    // Gérer les suggestions
    suggestionChips.forEach(chip => {
        chip.addEventListener('click', () => {
            userInput.value = chip.textContent;
            userInput.focus();
            
            // Trigger l'événement input pour ajuster la hauteur du textarea
            const event = new Event('input');
            userInput.dispatchEvent(event);
        });
    });

    // Envoi du message
    sendBtn.addEventListener('click', async () => {
        const question = userInput.value.trim();
        if (!question) return;

        // Désactiver le bouton pendant la requête
        sendBtn.disabled = true;
        sendBtn.classList.add('sending');

        // Ajouter le message utilisateur avec animation
        addMessage(question, 'user');
        userInput.value = '';
        userInput.style.height = '56px';
        userInput.focus();

        // Création et affichage de l'indicateur de saisie
        const typingIndicator = createTypingIndicator();
        messageContainer.appendChild(typingIndicator);
        scrollToBottom();

        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });

            // Supprimer l'indicateur de saisie
            messageContainer.removeChild(typingIndicator);

            const data = await response.json();
            if (data.error) {
                showError(data.error);
                return;
            }

            // Traiter la réponse Markdown
            const formattedResponse = marked.parse(data.response);
            
            // Ajouter animation de typage pour la réponse
            addMessageWithTypingEffect(formattedResponse, 'ai', data.sources);
        } catch (error) {
            console.error('Error:', error);
            messageContainer.removeChild(typingIndicator);
            showError('Erreur de connexion au serveur');
        } finally {
            // Réactiver le bouton d'envoi
            setTimeout(() => {
                sendBtn.disabled = false;
                sendBtn.classList.remove('sending');
            }, 500);
        }
    });

    function createTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'message ai-message animate__animated animate__fadeIn';
        div.innerHTML = `
            <div class="avatar ai-avatar">
                <div class="avatar-pulse"></div>
                <img src="${getRobotGifPath()}" alt="Robot médical" class="robot-gif">
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="dot-typing">
                        <div class="dot"></div>
                        <div class="dot"></div>
                        <div class="dot"></div>
                    </div>
                </div>
            </div>
        `;
        return div;
    }

    // Fonction pour obtenir le chemin du GIF du robot
    function getRobotGifPath() {
        const robotGif = document.querySelector('.robot-gif');
        return robotGif ? robotGif.src : "/static/robot_9066270.gif";
    }

    function addMessage(content, type, sources = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message animate__animated animate__fadeInUp`;
        
        const avatar = type === 'user' 
            ? `<div class="avatar user-avatar">
                <div class="avatar-pulse"></div>
                <div class="avatar-icon">👤</div>
               </div>`
            : `<div class="avatar ai-avatar">
                <div class="avatar-pulse"></div>
                <img src="${getRobotGifPath()}" alt="Robot médical" class="robot-gif">
               </div>`;

        const sourcesHTML = sources && sources.length > 0
            ? `<div class="medical-source">
                <span>Sources :</span>
                ${sources.map(s => `<div class="source-tag">${s}</div>`).join('')}
               </div>`
            : '';

        messageDiv.innerHTML = `
            ${avatar}
            <div class="message-content">
                ${content}
                ${sourcesHTML}
            </div>`;
        
        messageContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    // Fonction pour ajouter un message avec effet de saisie
    function addMessageWithTypingEffect(content, type, sources = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message animate__animated animate__fadeInUp`;
        
        const avatar = type === 'user' 
            ? `<div class="avatar user-avatar">
                <div class="avatar-pulse"></div>
                <div class="avatar-icon">👤</div>
               </div>`
            : `<div class="avatar ai-avatar">
                <div class="avatar-pulse"></div>
                <img src="${getRobotGifPath()}" alt="Robot médical" class="robot-gif">
               </div>`;

        const sourcesHTML = sources && sources.length > 0
            ? `<div class="medical-source">
                <span>Sources :</span>
                ${sources.map(s => `<div class="source-tag">${s}</div>`).join('')}
               </div>`
            : '';

        messageDiv.innerHTML = `
            ${avatar}
            <div class="message-content">
                <div class="typing-content"></div>
                ${sourcesHTML}
            </div>`;
        
        messageContainer.appendChild(messageDiv);
        scrollToBottom();
        
        // Animation du texte qui apparaît progressivement
        const typingContent = messageDiv.querySelector('.typing-content');
        animateTyping(content, typingContent);
    }
    
    // Animation de saisie lettre par lettre (effet de typage)
    function animateTyping(content, element) {
        // Créer un conteneur temporaire pour analyser le HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = content;
        
        // Si le contenu est complexe (avec HTML), afficher directement
        if (tempDiv.querySelectorAll('img, table, pre, ul, ol').length > 0) {
            element.innerHTML = content;
            scrollToBottom();
            return;
        }
        
        // Sinon, animation de typage pour le texte simple
        const text = tempDiv.textContent;
        const htmlContent = content;
        
        let i = 0;
        const speed = Math.max(10, 25 - (text.length / 100)); // Vitesse adaptative
        
        // Si le texte est très long, on skip l'animation
        if (text.length > 500) {
            element.innerHTML = htmlContent;
            scrollToBottom();
            return;
        }
        
        function typeWriter() {
            if (i < 30) {
                // Début de l'animation: afficher progressivement
                const progress = i / 30;
                const charsToShow = Math.floor(text.length * progress);
                element.textContent = text.substring(0, charsToShow) + '▋';
                i++;
                setTimeout(typeWriter, 20);
            } else {
                // Terminer avec le HTML complet pour conserver la mise en forme
                element.innerHTML = htmlContent;
            }
            scrollToBottom();
        }
        
        typeWriter();
    }

    function scrollToBottom() {
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message ai-message animate__animated animate__fadeIn';
        errorDiv.innerHTML = `
            <div class="avatar ai-avatar">
                <div class="avatar-icon" style="background:#ef4444">⚠️</div>
            </div>
            <div class="message-content">
                <div class="error-message">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <span>${message}</span>
                </div>
            </div>
        `;
        messageContainer.appendChild(errorDiv);
        scrollToBottom();
    }

    // Fonction pour formater les tableaux médicaments
    function formatMedicationTable(data) {
        if (!data || !Array.isArray(data)) return '';
        
        return `
        <div class="med-info-box">
            <div class="med-info-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"></path>
                </svg>
                Information médicament
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Nom</th>
                        <th>Dosage</th>
                        <th>Fréquence</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(med => `
                        <tr>
                            <td>${med.name}</td>
                            <td>${med.dosage}</td>
                            <td>${med.frequency}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>`;
    }

    // Animation initiale lors du chargement de la page
    function runStartupAnimations() {
        // Animation d'apparition progressive des éléments
        const elements = document.querySelectorAll('.app-header, .info-banner, .chat-container, .app-footer');
        
        elements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 100 * index);
        });
    }
    
    // Exécuter les animations de démarrage
    runStartupAnimations();
});