let allUsers = [];

// DOM Elements
const userGrid = document.getElementById('userGrid');
const searchInput = document.getElementById('searchInput');
const roleFilter = document.getElementById('roleFilter');
const jurisdictionFilter = document.getElementById('jurisdictionFilter');
const toast = document.getElementById('toast');

// Fetch data
async function loadUsers() {
    try {
        const response = await fetch('users.json');
        allUsers = await response.json();
        renderUsers(allUsers);
    } catch (error) {
        console.error("Failed to load users:", error);
        userGrid.innerHTML = `<p style="color:red; text-align:center; grid-column:1/-1">Failed to load user data. Ensure you are running via a server.</p>`;
    }
}

// Render Cards
function renderUsers(users) {
    userGrid.innerHTML = '';
    
    if(users.length === 0) {
        userGrid.innerHTML = `<p style="text-align:center; grid-column: 1/-1; color: var(--text-muted)">No users found.</p>`;
        return;
    }

    users.forEach(u => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <div class="card-header">
                <div class="card-name">${u.firstName} ${u.lastName}</div>
                <div class="badge">${u.designationCode}</div>
            </div>
            <div class="card-detail">Jur. Type: <span>${u.jurisdictionType}</span></div>
            <div class="card-detail">Jurisdiction: <span>${u.jurisdictionId}</span></div>
            <div class="card-detail">Email: <span>${u.email}</span></div>
            <button class="copy-btn" onclick="copyCreds('${u.email}')">Copy Login</button>
        `;
        userGrid.appendChild(card);
    });
}

// Filters
function applyFilters() {
    const searchTerm = searchInput.value.toLowerCase();
    const role = roleFilter.value;
    const jurisdiction = jurisdictionFilter.value;

    const filtered = allUsers.filter(u => {
        const matchesSearch = (u.firstName + ' ' + u.lastName + ' ' + u.email + ' ' + u.jurisdictionId).toLowerCase().includes(searchTerm);
        const matchesRole = role === 'ALL' || u.roleCode === role;
        const matchesJur = jurisdiction === 'ALL' || u.jurisdictionType === jurisdiction;
        return matchesSearch && matchesRole && matchesJur;
    });

    renderUsers(filtered);
}

// Event Listeners
searchInput.addEventListener('input', applyFilters);
roleFilter.addEventListener('change', applyFilters);
jurisdictionFilter.addEventListener('change', applyFilters);

// Copy functionality
window.copyCreds = function(email) {
    const textToCopy = `Email: ${email}\nPassword: Test@123`;
    navigator.clipboard.writeText(textToCopy).then(() => {
        showToast();
    });
};

function showToast() {
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 2000);
}

// Init
loadUsers();
