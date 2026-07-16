let allUsers = [];

const JUR_NAMES = {
  "1": "West Champaran", "3": "Patna",
  "464": "Patna (Sub-District)", "465": "Barh (Sub-District)", "466": "Masaurhi (Sub-District)", "467": "Danapur (Sub-District)", 
  "400": "Bagaha (Sub-District)", "401": "Narkatiaganj (Sub-District)", "402": "Bettiah Sadar (Sub-District)",
  "1960": "Patna Sadar", "1961": "Phulwari Sharif", "1962": "Naubatpur", "1963": "Maner", "1964": "Sampatchak", "1965": "Danapur", "1966": "Dhanarua",
  "1967": "Barh", "1968": "Athmalgola", "1969": "Bakhtiarpur", "1970": "Belchi", "1971": "Bihta", "1972": "Fatuha", "1973": "Khusrupur", "1974": "Mokama", "1975": "Pandarak",
  "1976": "Masaurhi", "1977": "Bikram", "1978": "Dulhin Bazar", "1979": "Daniyawan", "1980": "Paliganj", "1981": "Punpun",
  "1982": "Ghoswari",
  "1587": "Sidhaw", "1585": "Bagaha-I", "1586": "Bagaha-II", "1592": "Bhithaha", "1590": "Madhuban", "1589": "Piprasi", "1588": "Ramnagar", "1591": "Thakrah",
  "1594": "Gaunaha", "1596": "Lauriya", "1595": "Mainatand", "1593": "Narkatiaganj", "1597": "Sikta",
  "1598": "Bettiah", "1599": "Bairia", "1601": "Chanpatia", "1600": "Yogapatti", "1603": "Majhaulia", "1602": "Nautan",
  "549": "Sultanganj PS", "550": "Mussalahpur PS", "551": "Agamkuan PS", "552": "Chowk PS", "553": "Kankarbagh PS", "554": "Patrakar Nagar PS", "555": "Parsabazar PS", "556": "Panchrukhiya PS", "557": "Ramkrishnanagar PS", "558": "Masauri PS", "561": "Pipra PS", "562": "Gandhi Maidan PS", "563": "Kadamkuan PS", "564": "Pirbahore PS", "565": "Kotwali PS", "566": "Patliputra PS", "567": "Digha PS", "568": "Rajivnagar PS", "569": "Gardnibagh PS", "570": "Sachiwalay PS", "571": "Shastrinagar PS", "572": "Srikrishnapuri PS", "574": "Khagaul PS", "575": "Shahpur PS", "576": "Rupaspur PS", "579": "Neura PS", "580": "Phulwarisharif PS", "582": "Piplawan (Pitwas) PS", "584": "Sigori PS", "586": "Raniatalab PS", "588": "Imamganj PS", "589": "Piarpura PS", "590": "Didarganj PS", "592": "Daniyawa PS", "593": "Shahjahapur PS", "594": "Nadi PS", "597": "Bakhtiyarpur PS", "581": "Naubatpur PS", "577": "Maner PS", "573": "Danapur PS", "559": "Dhanarua PS", "595": "Barh PS", "578": "Bihta PS", "591": "Fatuha PS", "596": "Mokama PS", "587": "Bikram PS", "585": "Dulhin Bazar PS", "583": "Paliganj PS", "560": "Punpun PS", "852": "Pathkhauli Sivir PS", "851": "Bagaha PS", "853": "Chautarwa PS", "854": "Bhairoganj Sahayak (Naxal) PS", "855": "SC/ ST PS", "863": "Chiutahan (Naxal) PS", "856": "Nadi PS", "859": "Bhithan PS", "857": "Dhanhan PS", "860": "Piprasi PS", "861": "Ramnagar PS", "858": "Thakrahan PS", "872": "Gaunaha PS", "869": "Lauriya PS", "873": "Mainatand PS", "871": "Narkatiaganj PS", "874": "Sikta PS", "864": "Bettiah PS", "865": "Mufassil PS", "866": "Kalibagh PS", "862": "Bathwaria (sahayak) PS", "870": "Chanpatia PS", "867": "Yogapatti PS", "868": "Nawalpur PS", "877": "Sanichari PS", "878": "Srinagar PS", "875": "Majhaulia PS", "876": "Nautan PS"
};

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
            <div class="card-detail">Jurisdiction: <span>${JUR_NAMES[u.jurisdictionId] ? JUR_NAMES[u.jurisdictionId] + ' (' + u.jurisdictionId + ')' : u.jurisdictionId}</span></div>
            <div class="card-detail">Email: <span>${u.email}</span></div>
            <div class="card-detail">ID: <span style="font-size:11px; word-break:break-all;">${u.userId || 'N/A'}</span></div>
            <button class="copy-btn" onclick="copyCreds('${u.email}', '${u.userId || ''}')">Copy Login</button>
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
        const jurName = JUR_NAMES[u.jurisdictionId] || "";
        const matchesSearch = (u.firstName + ' ' + u.lastName + ' ' + u.email + ' ' + u.jurisdictionId + ' ' + jurName + ' ' + (u.userId || '')).toLowerCase().includes(searchTerm);
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
window.copyCreds = function(email, userId) {
    const textToCopy = `Email: ${email}\nPassword: Test@123\nUser ID: ${userId}`;
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
