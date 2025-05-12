document.addEventListener("DOMContentLoaded", () => {
    const messageContainer = document.getElementById("messageContainer");
    const userInput = document.getElementById("userInput");
    const sendBtn = document.getElementById("sendBtn");
    const themeToggle = document.getElementById("themeToggle");
    const suggestionChips = document.querySelectorAll(".chip");
    const mediaBtn = document.getElementById("mediaBtn");
    const mediaOptions = document.getElementById("mediaOptions");
    const cameraOption = document.getElementById("cameraOption");
    const uploadOption = document.getElementById("uploadOption");
    const fileInput = document.getElementById("fileInput");
    const robotImagePath = document.getElementById("appConfig").getAttribute("data-robot-image");

    // Références modale caméra
    const cameraModal = document.getElementById("cameraModal");
    const videoElement = document.getElementById("videoElement");
    const capturedImageContainer = document.getElementById("capturedImageContainer");
    const capturedImage = document.getElementById("capturedImage");
    const captureBtn = document.getElementById("captureBtn");
    const useBtn = document.getElementById("useBtn");
    const retakeBtn = document.getElementById("retakeBtn");
    const processingIndicator = document.getElementById("processingIndicator");
    const medicationResult = document.getElementById("medicationResult");
    const medicationName = document.getElementById("medicationName");
    const medicationDesc = document.getElementById("medicationDesc");
    const closeModal = document.querySelector(".close-modal");
  
    let stream = null;
    let capturedData = null;
  
    // Gestion média
    mediaBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        mediaOptions.classList.toggle("show");
        
        // Debug pour voir si l'événement est déclenché
        console.log("Media button clicked, dropdown visibility:", mediaOptions.classList.contains("show"));
    });
  
    document.addEventListener("click", (e) => {
        if (!mediaOptions.contains(e.target) && e.target !== mediaBtn) {
          mediaOptions.classList.remove("show");
        }
    });
  
    cameraOption.addEventListener("click", () => {
      mediaOptions.classList.remove("show");
      openCameraModal();
    });
  
    uploadOption.addEventListener("click", () => {
        mediaOptions.classList.remove("show");
        // Réinitialiser le fileInput pour permettre la sélection répétée du même fichier
        fileInput.value = "";
        fileInput.click();
    });
    
    function initUI() {
        // Autres initialisations...
        mediaOptions.classList.remove("show");
    }
      
    // Appeler initUI au chargement du document
    document.addEventListener("DOMContentLoaded", initUI);
    
    fileInput.addEventListener("change", (e) => {
        if (fileInput.files[0]) {
          const reader = new FileReader();
          reader.onload = (e) => {
            // Réinitialiser tous les états précédents avant d'ouvrir le modal
            medicationName.textContent = "";
            medicationDesc.textContent = "";
            medicationResult.style.display = "none";
            
            // Maintenant ouvrir le modal avec l'image préchargée
            openCameraModal(e.target.result);
          };
          reader.readAsDataURL(fileInput.files[0]);
        }
    });
  
    // Fonctions caméra
    function openCameraModal(preloadedImage = null) {
        cameraModal.style.display = "block";
        
        // Réinitialiser l'UI d'abord
        resetCameraUI();
        
        if (preloadedImage) {
          showCapturedImage(preloadedImage);
          // Attendre un petit instant avant de lancer l'analyse pour s'assurer que l'UI est mise à jour
          setTimeout(() => {
            updateModalSteps("analyze");
            analyzeImage(preloadedImage);
          }, 100);
        } else {
          startCamera();
          updateModalSteps("capture");
        }
    }
  
    async function startCamera() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment" }
        });
        videoElement.srcObject = stream;
        resetCameraUI();
      } catch (err) {
        console.error("Erreur caméra:", err);
        alert("Accès à la caméra refusé!");
        closeCameraModal();
      }
    }
  
    function resetCameraUI() {
      videoElement.style.display = "block";
      capturedImageContainer.style.display = "none";
      captureBtn.style.display = "block";
      useBtn.style.display = "none";
      retakeBtn.style.display = "none";
      medicationResult.style.display = "none";
      processingIndicator.style.display = "none";
    }
  
    function showCapturedImage(imageData) {
      videoElement.style.display = "none";
      capturedImageContainer.style.display = "block";
      capturedImage.src = imageData;
      captureBtn.style.display = "none";
      useBtn.style.display = "block";
      retakeBtn.style.display = "block";
    }
  
    function closeCameraModal() {
      cameraModal.style.display = "none";
      stopCamera();
      resetCameraUI();
    }
  
    function stopCamera() {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
      }
    }
  
    // Capture d'image
    captureBtn.addEventListener("click", () => {
      const canvas = document.createElement("canvas");
      canvas.width = videoElement.videoWidth;
      canvas.height = videoElement.videoHeight;
      canvas.getContext("2d").drawImage(videoElement, 0, 0);
      capturedData = canvas.toDataURL("image/jpeg");
      
      showCapturedImage(capturedData);
      processingIndicator.style.display = "block";
      updateModalSteps("analyze");
      analyzeImage(capturedData);
    });
  
    // Analyse d'image
    async function analyzeImage(imageData) {
        try {
          processingIndicator.style.display = "block";
          
          const response = await fetch("/analyze-medication", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: imageData })
          });
          
          const data = await response.json();
          processingIndicator.style.display = "none";
      
          if (data.success) {
            // Effacer les anciennes données avant d'afficher les nouvelles
            medicationName.textContent = data.medication_name;
            medicationDesc.textContent = data.description || "";
            medicationResult.style.display = "block";
            updateModalSteps("result");
          } else {
            throw new Error("Aucun médicament détecté");
          }
        } catch (error) {
          console.error("Erreur analyse:", error);
          processingIndicator.style.display = "none";
          medicationResult.style.display = "none";
          showError(error.message);
          updateModalSteps("capture");
        }
    }
    
    function closeAndResetCameraModal() {
        cameraModal.style.display = "none";
        stopCamera();
        resetCameraUI();
        // Réinitialiser également les résultats
        medicationName.textContent = "";
        medicationDesc.textContent = "";
        medicationResult.style.display = "none";
    }
    
    // Gestion modale
    closeModal.addEventListener("click", closeCameraModal);
    window.addEventListener("click", (e) => e.target === cameraModal && closeCameraModal());
  
    retakeBtn.addEventListener("click", () => {
      startCamera();
      updateModalSteps("capture");
    });
  
    useBtn.addEventListener("click", () => {
        if (medicationName.textContent) {
          userInput.value = `Informations sur ${medicationName.textContent} ${medicationDesc.textContent}`;
          closeAndResetCameraModal();
          setTimeout(() => sendBtn.click(), 300);
        }
    });
  
    function updateModalSteps(step) {
      const steps = {
        capture: ["active", "", ""],
        analyze: ["completed", "active", ""],
        result: ["completed", "completed", "active"]
      };
      
      document.querySelectorAll(".step").forEach((el, i) => 
        el.className = `step ${steps[step][i]}`);
    }
  
    // Thème
    function initTheme() {
      const savedTheme = localStorage.getItem("theme");
      const systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      document.documentElement.setAttribute("data-theme",
        savedTheme || (systemDark ? "dark" : "light"));
    }
  
    themeToggle.addEventListener("click", () => {
      const newTheme = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
      document.documentElement.classList.add("theme-transition");
      document.documentElement.setAttribute("data-theme", newTheme);
      localStorage.setItem("theme", newTheme);
      setTimeout(() => document.documentElement.classList.remove("theme-transition"), 300);
    });
    
    // Chat
    userInput.addEventListener("input", function() {
        // Sauvegarder la position du curseur
        const selectionStart = this.selectionStart;
        const selectionEnd = this.selectionEnd;
        
        // Ajuster la hauteur avec un délai pour éviter les conflits de rendu
        requestAnimationFrame(() => {
          this.style.height = "auto";
          const newHeight = Math.min(this.scrollHeight, 200);
          this.style.height = newHeight + "px";
          
          // Restaurer la position du curseur
          this.setSelectionRange(selectionStart, selectionEnd);
        });
    });
  
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          handleSend();  // Appeler la fonction directement au lieu de cliquer sur le bouton
        }
    });
  
    // Ajouter l'event listener au bouton d'envoi
    sendBtn.addEventListener("click", handleSend);

    sendBtn.addEventListener("mousedown", function() {
      const ripple = this.querySelector(".send-ripple");
      if (ripple) {
        ripple.style.cssText = "opacity:1; transform:scale(0)";
        setTimeout(() => {
          ripple.style.transform = "scale(4)";
          setTimeout(() => ripple.style.opacity = "0", 300);
        }, 10);
      }
    });
  
    suggestionChips.forEach(chip => chip.addEventListener("click", () => {
      userInput.value = chip.textContent;
      userInput.dispatchEvent(new Event("input"));
      userInput.focus();
    }));
  
    // Fonction pour ajouter un message avec effet de frappe
    function addMessageWithTypingEffect(content, type, sources = []) {
      const messageDiv = document.createElement("div");
      messageDiv.className = `message ${type}-message animate__animated animate__fadeInUp`;
      messageDiv.style.animationDuration = "0.4s";
      
      const avatar = type === "user" 
        ? "👤" 
        : `<img src="${robotImagePath}" class="robot-gif">`;
      
      messageDiv.innerHTML = `
        <div class="avatar ${type}-avatar">
          <div class="avatar-pulse"></div>
          ${avatar}
        </div>
        <div class="message-content">
          <p class="typing-content"></p>
          ${sources.length ? `<div class="medical-source">
            <span>Sources :</span>${sources.map(s => `<div class="source-tag">${s}</div>`).join("")}
          </div>` : ""}
        </div>`;
      
      messageContainer.appendChild(messageDiv);
      
      const typingElement = messageDiv.querySelector(".typing-content");
      
      // Add entrance animation to the message
      messageDiv.style.opacity = "0";
      messageDiv.style.transform = "translateY(20px)";
      
      setTimeout(() => {
        messageDiv.style.transition = "opacity 0.4s ease, transform 0.4s ease";
        messageDiv.style.opacity = "1";
        messageDiv.style.transform = "translateY(0)";
        
        // Start typing animation after the message appears
        setTimeout(() => animateTyping(content, typingElement), 200);
      }, 50);
      
      scrollToBottom();
    }
  
    // Envoi messages
    async function handleSend() {
        const question = userInput.value.trim();
        if (!question) return;
      
        addMessage(question, "user");
        userInput.value = "";
        userInput.style.height = "56px";
      
        const typingIndicator = createTypingIndicator();
        messageContainer.appendChild(typingIndicator);
        scrollToBottom();
      
        try {
          const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
          });
          
          const data = await response.json();
          messageContainer.removeChild(typingIndicator);
      
          if (data.error) throw new Error(data.error);
          
          // Apply table enhancements before displaying
          const enhancedContent = enhanceTableDisplay(marked.parse(data.response));
          
          addMessageWithTypingEffect(
            enhancedContent, 
            "ai", 
            data.sources
          );
        } catch (error) {
          showError(error.message);
        }
    }
  
    // Helpers
    function createTypingIndicator() {
      const div = document.createElement("div");
      div.className = "message ai-message animate__animated animate__fadeIn";
      div.style.animationDuration = "0.3s";
      
      div.innerHTML = `
        <div class="avatar ai-avatar">
          <div class="avatar-pulse"></div>
          <img src="${robotImagePath}" class="robot-gif">
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <div class="dot-typing">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </div>
        </div>`;
      
      const avatar = div.querySelector(".avatar");
      avatar.style.animation = "ai-thinking 1.5s infinite";
      
      return div;
    }
  
    function addMessage(content, type, sources = []) {
      const messageDiv = document.createElement("div");
      messageDiv.className = `message ${type}-message animate__animated animate__fadeInUp`;
      messageDiv.innerHTML = `
        <div class="avatar ${type}-avatar">
          <div class="avatar-pulse"></div>
          ${type === "user" ? "👤" : `<img src="${robotImagePath}" class="robot-gif">`}
        </div>
        <div class="message-content">
          ${type === "user" ? `<p>${content}</p>` : content}
          ${sources.length ? `<div class="medical-source">
            <span>Sources :</span>${sources.map(s => `<div class="source-tag">${s}</div>`).join("")}
          </div>` : ""}
        </div>`;
      messageContainer.appendChild(messageDiv);
      scrollToBottom();
    }

  
    function animateTyping(content, element) {
      let i = 0;
      const text = new DOMParser().parseFromString(content, "text/html").body.textContent;
      let typingSpeed = 5; // Faster typing speed (milliseconds)
      
      // Check if the content contains a table and handle it differently
      if (content.includes("<table>")) {
        // For tables, don't animate typing but rather fade in with a scale effect
        element.innerHTML = content;
        const tables = element.querySelectorAll("table");
        tables.forEach(table => {
          table.style.opacity = "0";
          table.style.transform = "scale(0.95)";
          setTimeout(() => {
            table.style.transition = "opacity 0.5s ease, transform 0.5s ease";
            table.style.opacity = "1";
            table.style.transform = "scale(1)";
          }, 100);
        });
        return;
      }
      
      function typeWriter() {
        if (i < text.length) {
          // Type characters faster when certain punctuation is encountered
          const char = text.charAt(i);
          element.innerHTML = text.substring(0, i++) + "▋";
          
          // Adjust typing speed based on character
          if (char === '.' || char === '!' || char === '?') {
            setTimeout(typeWriter, typingSpeed * 5); // Pause longer at end of sentences
          } else if (char === ',' || char === ';') {
            setTimeout(typeWriter, typingSpeed * 3); // Pause briefly at commas
          } else {
            setTimeout(typeWriter, typingSpeed); // Normal typing speed
          }
        } else {
          element.innerHTML = content; // Replace with formatted content
          
          // Add animation to specific elements after typing is complete
          setTimeout(() => {
            const lists = element.querySelectorAll("ul, ol");
            const codeBlocks = element.querySelectorAll("pre, code");
            
            lists.forEach((list, index) => {
              list.style.animation = `fade-in-up 0.5s ease forwards ${index * 0.1}s`;
              list.style.opacity = "0";
            });
            
            codeBlocks.forEach((block, index) => {
              block.style.animation = `scale-in 0.5s ease forwards ${index * 0.1}s`;
              block.style.opacity = "0";
            });
          }, 200);
        }
        scrollToBottom();
      }
      
      typeWriter();
    }
  
    function scrollToBottom() {
      messageContainer.scrollTo({
        top: messageContainer.scrollHeight,
        behavior: 'smooth'
      });
    }
  
    function showError(message) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "message ai-message animate__animated animate__fadeIn";
      errorDiv.innerHTML = `
        <div class="avatar ai-avatar">⚠️</div>
        <div class="message-content">
          <div class="error-message">
            <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
            <span>${message}</span>
          </div>
        </div>`;
      messageContainer.appendChild(errorDiv);
      scrollToBottom();
    }
  
    // Add function to detect tables in the response and enhance them
    function enhanceTableDisplay(content) {
      // Check if the content has a table
      if (content.includes("<table>")) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(content, 'text/html');
        const tables = doc.querySelectorAll('table');
        
        tables.forEach(table => {
          // Add responsive class
          table.classList.add('responsive-table');
          
          // Add zebra striping
          const rows = table.querySelectorAll('tr');
          rows.forEach((row, index) => {
            if (index % 2 === 0) {
              row.classList.add('even-row');
            } else {
              row.classList.add('odd-row');
            }
          });
        });
        
        return doc.body.innerHTML;
      }
      
      return content;
    }
  
    // Initialisation
    initTheme();
    document.querySelectorAll(".app-header, .info-banner, .chat-container, .app-footer")
      .forEach((el, i) => {
        el.style.opacity = "0";
        el.style.transform = "translateY(20px)";
        setTimeout(() => {
          el.style.opacity = "1";
          el.style.transform = "translateY(0)";
        }, 100 * i);
      });
});