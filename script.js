// DOM Elements
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebarToggle');
const fab = document.getElementById('fab');
const modal = document.getElementById('newNotebookModal');
const modalClose = document.getElementById('modalClose');
const cancelBtn = document.getElementById('cancelBtn');
const createBtn = document.getElementById('createBtn');

// Sidebar Toggle
sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
});

// Sidebar Items
document.querySelectorAll('.sidebar-item').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
    });
});

// Action Cards
document.querySelectorAll('.action-card').forEach(card => {
    card.addEventListener('click', () => {
        const action = card.dataset.action;
        if (action === 'new-notebook') {
            showModal();
        } else {
            // Handle other actions
            console.log(`Action: ${action}`);
        }
    });
});

// Notebook Cards
document.querySelectorAll('.notebook-card:not(.create-new)').forEach(card => {
    card.addEventListener('click', () => {
        // Navigate to notebook
        console.log('Opening notebook...');
    });
});

// Create New Notebook Card
document.querySelector('.notebook-card.create-new').addEventListener('click', showModal);

// FAB
fab.addEventListener('click', () => {
    // Open quick chat
    console.log('Opening quick chat...');
});

// Modal Functions
function showModal() {
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function hideModal() {
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
    // Clear form
    document.getElementById('notebookName').value = '';
    document.getElementById('notebookDescription').value = '';
}

// Modal Event Listeners
modalClose.addEventListener('click', hideModal);
cancelBtn.addEventListener('click', hideModal);

// Close modal on backdrop click
modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        hideModal();
    }
});

// Create Notebook
createBtn.addEventListener('click', () => {
    const name = document.getElementById('notebookName').value.trim();
    const description = document.getElementById('notebookDescription').value.trim();
    
    if (!name) {
        alert('Please enter a notebook name');
        return;
    }
    
    // Here you would typically make an API call to create the notebook
    console.log('Creating notebook:', { name, description });
    
    // Show success animation
    createBtn.innerHTML = '✓ Created!';
    createBtn.style.background = 'linear-gradient(135deg, #10B981, #059669)';
    
    setTimeout(() => {
        hideModal();
        createBtn.innerHTML = 'Create Notebook';
        createBtn.style.background = '';
        // Add new notebook to the grid (you would refresh from API)
        addNotebookToGrid(name, description);
    }, 1000);
});

// Add notebook to grid (demo function)
function addNotebookToGrid(name, description) {
    const grid = document.querySelector('.notebooks-grid');
    const createCard = document.querySelector('.notebook-card.create-new');
    
    const newCard = document.createElement('div');
    newCard.className = 'notebook-card';
    newCard.innerHTML = `
        <div class="notebook-header">
            <div class="notebook-icon">📒</div>
            <div class="notebook-menu">⋯</div>
        </div>
        <div class="notebook-content">
            <h3 class="notebook-title">${name}</h3>
            <p class="notebook-description">${description}</p>
            <div class="notebook-stats">
                <span class="stat">0 sources</span>
                <span class="stat">0 notes</span>
                <span class="stat">0 insights</span>
            </div>
        </div>
        <div class="notebook-footer">
            <span class="notebook-date">Just created</span>
            <div class="notebook-actions">
                <button class="btn-icon">💬</button>
                <button class="btn-icon">🎙️</button>
            </div>
        </div>
    `;
    
    // Insert before the create card
    grid.insertBefore(newCard, createCard);
    
    // Add click handler
    newCard.addEventListener('click', () => {
        console.log(`Opening notebook: ${name}`);
    });
    
    // Animate in
    newCard.style.opacity = '0';
    newCard.style.transform = 'translateY(20px)';
    setTimeout(() => {
        newCard.style.transition = 'all 0.5s ease';
        newCard.style.opacity = '1';
        newCard.style.transform = 'translateY(0)';
    }, 100);
}

// Particles Animation
function createParticles() {
    const container = document.getElementById('particles');
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random position
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        
        // Random animation delay
        particle.style.animationDelay = Math.random() * 6 + 's';
        
        // Random size
        const size = Math.random() * 3 + 1;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        
        container.appendChild(particle);
    }
}

// Mouse Movement Effect
let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX / window.innerWidth;
    mouseY = e.clientY / window.innerHeight;
    
    // Update background gradient based on mouse position
    const bg = document.querySelector('.animated-bg');
    const offsetX = (mouseX - 0.5) * 20;
    const offsetY = (mouseY - 0.5) * 20;
    
    bg.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(1.05)`;
});

// Intersection Observer for Animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all cards for scroll animations
document.addEventListener('DOMContentLoaded', () => {
    // Initialize particles
    createParticles();
    
    // Set up scroll animations
    document.querySelectorAll('.stat-card, .action-card, .notebook-card, .activity-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
    
    // Stagger animations
    document.querySelectorAll('.stat-card').forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        console.log('Open search...');
    }
    
    // Ctrl/Cmd + N for new notebook
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        showModal();
    }
    
    // Escape to close modal
    if (e.key === 'Escape' && modal.classList.contains('show')) {
        hideModal();
    }
});

// Add ripple effect to buttons
document.querySelectorAll('button, .action-card, .notebook-card').forEach(element => {
    element.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        this.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
});

// Add ripple CSS
const rippleCSS = `
.ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(0, 255, 255, 0.3);
    transform: scale(0);
    animation: ripple-animation 0.6s linear;
    pointer-events: none;
}

@keyframes ripple-animation {
    to {
        transform: scale(4);
        opacity: 0;
    }
}
`;

const style = document.createElement('style');
style.textContent = rippleCSS;
document.head.appendChild(style);

// Smooth scrolling for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading states
function showLoading(element) {
    element.classList.add('loading');
    element.style.pointerEvents = 'none';
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.style.pointerEvents = 'auto';
}

// Performance optimization: Throttle mouse movement
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Apply throttling to mouse movement
document.addEventListener('mousemove', throttle((e) => {
    mouseX = e.clientX / window.innerWidth;
    mouseY = e.clientY / window.innerHeight;
    
    const bg = document.querySelector('.animated-bg');
    const offsetX = (mouseX - 0.5) * 15;
    const offsetY = (mouseY - 0.5) * 15;
    
    bg.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(1.02)`;
}, 16)); // ~60fps