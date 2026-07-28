document.addEventListener('DOMContentLoaded', () => {
    // Login & Logout
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: document.getElementById('username').value,
                    password: document.getElementById('password').value
                })
            });
            if (res.ok) window.location.reload();
            else document.getElementById('login-err').textContent = 'Invalid ID/Password';
        });
    }

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            await fetch('/api/logout', { method: 'POST' });
            window.location.reload();
        });
    }

    
    // Load initial data for logged-in admin
    if (document.getElementById('profile-form')) {
        loadProfile();
        loadSkills();
        loadExperience();
        loadProjects();

        // 1. Profile Update
        document.getElementById('profile-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await fetch('/api/profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: document.getElementById('prof-name').value,
                    role: document.getElementById('prof-role').value,
                    bio: document.getElementById('prof-bio').value,
                    email: document.getElementById('prof-email').value,
                    phone: document.getElementById('prof-phone').value,
                    github: document.getElementById('prof-github').value,
                    linkedin: document.getElementById('prof-linkedin').value
                })
            });
            alert('Profile updated successfully!');
        });

        // 2. Add Skill
        document.getElementById('skill-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await fetch('/api/skills', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: document.getElementById('sk-name').value,
                    percentage: document.getElementById('sk-perc').value
                })
            });
            document.getElementById('skill-form').reset();
            loadSkills();
        });

        // 3. Add Experience
        document.getElementById('exp-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await fetch('/api/experience', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: document.getElementById('exp-title').value,
                    company: document.getElementById('exp-company').value,
                    period: document.getElementById('exp-period').value,
                    description: document.getElementById('exp-desc').value
                })
            });
            document.getElementById('exp-form').reset();
            loadExperience();
        });

        // 4. Add Project
        document.getElementById('project-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await fetch('/api/projects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: document.getElementById('proj-title').value,
                    description: document.getElementById('proj-desc').value,
                    tech_stack: document.getElementById('proj-tech').value.split(','),
                    image_url: document.getElementById('proj-img').value,
                    github_url: document.getElementById('proj-github').value,
                    demo_url: document.getElementById('proj-demo').value
                })
            });
            document.getElementById('project-form').reset();
            loadProjects();
        });
    }
});

async function loadProfile() {
    const res = await fetch('/api/profile');
    const data = await res.json();
    document.getElementById('prof-name').value = data.name || '';
    document.getElementById('prof-role').value = data.role || '';
    document.getElementById('prof-bio').value = data.bio || '';
    document.getElementById('prof-email').value = data.email || '';
    document.getElementById('prof-phone').value = data.phone || '';
    document.getElementById('prof-github').value = data.github || '';
    document.getElementById('prof-linkedin').value = data.linkedin || '';
}

async function loadSkills() {
    const res = await fetch('/api/skills');
    const data = await res.json();
    document.getElementById('skills-list').innerHTML = data.map(s => `
        <div class="data-row">
            <span><strong>${s.name}</strong> (${s.percentage}%)</span>
            <button class="btn-del" onclick="deleteSkill(${s.id})">Delete</button>
        </div>
    `).join('');
}

async function loadExperience() {
    const res = await fetch('/api/experience');
    const data = await res.json();
    document.getElementById('exp-list').innerHTML = data.map(e => `
        <div class="data-row">
            <span><strong>${e.title}</strong> at ${e.company}</span>
            <button class="btn-del" onclick="deleteExp(${e.id})">Delete</button>
        </div>
    `).join('');
}

async function loadProjects() {
    const res = await fetch('/api/projects');
    const data = await res.json();
    document.getElementById('projects-list').innerHTML = data.map(p => `
        <div class="data-row">
            <span><strong>${p.title}</strong></span>
            <button class="btn-del" onclick="deleteProj(${p.id})">Delete</button>
        </div>
    `).join('');
}

window.deleteSkill = async (id) => { await fetch(`/api/skills/${id}`, { method: 'DELETE' }); loadSkills(); };
window.deleteExp = async (id) => { await fetch(`/api/experience/${id}`, { method: 'DELETE' }); loadExperience(); };
window.deleteProj = async (id) => { await fetch(`/api/projects/${id}`, { method: 'DELETE' }); loadProjects(); };