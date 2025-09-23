// Mobile menu toggle
document.getElementById('menu-btn').addEventListener('click', function() {
    const menu = document.getElementById('mobile-menu');
    menu.classList.toggle('hidden');
});

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const menu = document.getElementById('mobile-menu');
    const menuBtn = document.getElementById('menu-btn');
    
    if (!menu.contains(event.target) && !menuBtn.contains(event.target)) {
        menu.classList.add('hidden');
    }
});

// --- ANIMASI TYPING UNTUK HERO SECTION ---
document.addEventListener('DOMContentLoaded', () => {
    // Pastikan elemen ada sebelum menjalankan script
    if (document.getElementById('typed-text')) {
        var options = {
            strings: [
                'Rafli Damara...',
                'a Data Scientist...',
                'a Data Analyst...',
                'an AI Engineer...'
            ],
            typeSpeed: 50,    // Kecepatan mengetik (ms)
            backSpeed: 25,    // Kecepatan menghapus (ms)
            loop: true,       // Ulangi animasi
            showCursor: true,
            cursorChar: '|',
        };

        var typed = new Typed('#typed-text', options);
    }

    // Kode animasi intro section yang baru ditambahkan
    const sections = document.querySelectorAll('.section-intro');

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target); // Berhenti mengamati setelah animasi selesai
            }
        });
    }, {
        threshold: 0.2 // Ubah nilai ini sesuai kebutuhan
    });

    sections.forEach(section => {
        observer.observe(section);
    });
    // Akhir kode animasi intro section

});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        if (this.getAttribute('href') === '#') return;
        
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            // Close mobile menu if open
            document.getElementById('mobile-menu').classList.add('hidden');
            
            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    });
});

// Animation for stats counters
function animateCounters() {
    const counters = document.querySelectorAll('.counter');
    const speed = 100; // Kecepatan animasi (semakin kecil, semakin cepat)

    counters.forEach(counter => {
        const target = +counter.getAttribute('data-target');
        let count = 0; // Mulai dari 0
        const increment = Math.ceil(target / 20); // Jumlah kenaikan setiap interval

        function updateCounter() {
            const randomValue = Math.floor(Math.random() * target); // Angka acak
            counter.innerText = randomValue;

            if (count < target) {
                count += increment;
                if (count > target) {
                    counter.innerText = target; // Pastikan mencapai target
                } else {
                    setTimeout(updateCounter, speed);
                }
            } else {
                counter.innerText = target; // Set nilai akhir
            }
        }

        updateCounter();
    });
}

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-fade-in');
            
            // If it's a stats section, animate counters
            if (entry.target.id === 'stats') {
                animateCounters();
                observer.unobserve(entry.target); // Unobserve setelah animasi selesai
            }
            
        }
    });
}, observerOptions);

// Observe elements for animation
document.addEventListener('DOMContentLoaded', function() {
    const elementsToAnimate = document.querySelectorAll('.skill-bar, .project-card, .experience-item');
    elementsToAnimate.forEach(el => {
        observer.observe(el);
    });

    // Observe the stats section
    const statsSection = document.getElementById('stats');
    if (statsSection) {
        observer.observe(statsSection);
    }
});

// static/js/script.js

// --- LOGIKA FUNGSIONALITAS CHATBOT ---
document.addEventListener('DOMContentLoaded', () => {
    const chatLog = document.getElementById('chat-log');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');

    if (chatInput) {
        sendBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    function sendMessage() {
        const message = chatInput.value.trim();
        if (message === '') return;

        // Tampilkan pesan pengguna di log
        appendMessage('user', message);
        chatInput.value = '';

        // Tampilkan indikator "thinking"
        appendThinkingIndicator();

        // Kirim pesan ke backend Flask
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        })
        .then(response => response.json())
        .then(data => {
            // Hapus indikator "thinking"
            removeThinkingIndicator();
            // Tampilkan balasan dari bot
            appendMessage('assistant', data.response);
        })
        .catch((error) => {
            removeThinkingIndicator();
            appendMessage('assistant', 'Sorry, there was an error connecting to the server.');
            console.error('Error:', error);
        });
    }

    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('flex', sender === 'user' ? 'justify-end' : 'justify-start');

        const messageBubble = document.createElement('div');
        messageBubble.classList.add(sender === 'user' ? 'bg-primary' : 'bg-gray-600', 'text-white', 'p-3', 'rounded-lg', 'max-w-xs');

        const messageText = document.createElement('p');
        messageText.classList.add('text-sm');
        messageText.textContent = text;

        messageBubble.appendChild(messageText);
        messageDiv.appendChild(messageBubble);
        chatLog.appendChild(messageDiv);

        // Auto-scroll ke pesan terbaru
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function appendThinkingIndicator() {
        const thinkingDiv = document.createElement('div');
        thinkingDiv.id = 'thinking-indicator';
        thinkingDiv.classList.add('flex', 'items-center', 'space-x-2');
        thinkingDiv.innerHTML = `
            <i class="fas fa-robot text-primary text-xl"></i>
            <p class="text-sm text-gray-400 animate-pulse">Bentar mikir dulu yaa...</p>
        `;
        chatLog.appendChild(thinkingDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function removeThinkingIndicator() {
        const indicator = document.getElementById('thinking-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
});