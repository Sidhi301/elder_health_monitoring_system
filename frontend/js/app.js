

document.addEventListener("DOMContentLoaded", () => {
    const page = document.body.dataset.page;
    attachLogout();

    if (page === "login") {
        setupLoginPage();
    }

    if (page === "register") {
        setupRegisterPage();
    }

    if (page === "dashboard") {
        setupDashboardPage();
    }

    if (page === "add-health") {
        setupAddHealthPage();
    }

    if (page === "alerts") {
        setupAlertsPage();
    }

    if (page === "patient-data") {
        setupPatientDataPage();
    }

    if (page === "emergency") {
        setupEmergencyPage();
    }
});

function attachLogout() {
    const logoutButton = document.getElementById("logoutButton");
    if (logoutButton) {
        logoutButton.addEventListener("click", logoutUser);
    }
}

function setMessage(elementId, text, isError = false) {
    const element = document.getElementById(elementId);
    if (!element) {
        return;
    }
    element.textContent = text;
    element.style.color = isError ? "#c44536" : "#1f6f8b";
}

function formatRole(role) {
    return role.replace("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatDate(dateText) {
    if (!dateText) {
        return "No date";
    }
    return new Date(dateText).toLocaleString();
}

function toggleCareManagerSecretField() {
    const roleSelect = document.getElementById("registerRole");
    const secretGroup = document.getElementById("careManagerSecretGroup");
    const secretInput = document.getElementById("careManagerSecret");

    if (!roleSelect || !secretGroup || !secretInput) {
        return;
    }

    const isCareManager = roleSelect.value === "care_manager";
    secretGroup.classList.toggle("hidden", !isCareManager);
    secretInput.required = isCareManager;

    if (!isCareManager) {
        secretInput.value = "";
    }
}

async function loadPatients() {
    const data = await apiRequest("/api/patients");
    return data.patients || [];
}

function fillPatientSelect(selectId, patients, placeholder) {
    const select = document.getElementById(selectId);
    if (!select) {
        return;
    }

    select.innerHTML = "";

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = placeholder;
    select.appendChild(defaultOption);

    patients.forEach((patient) => {
        const option = document.createElement("option");
        option.value = patient.patient_code;
        option.textContent = `${patient.patient_code} - ${patient.name} (Age ${patient.age})`;
        select.appendChild(option);
    });
}

function renderPatients(patientList, patients) {
    patientList.innerHTML = "";

    if (patients.length === 0) {
        patientList.innerHTML = "<p>No linked patients found.</p>";
        return;
    }

    patients.forEach((patient) => {
        const item = document.createElement("div");
        item.className = "list-item";
        item.innerHTML = `
            <h3>${patient.name}</h3>
            <p><strong>Patient Code:</strong> ${patient.patient_code}</p>
            <p><strong>Age:</strong> ${patient.age}</p>
            <p><strong>Parent Code:</strong> ${patient.parent_user_code}</p>
            <p><strong>Child Code:</strong> ${patient.child_user_code || "Not linked"}</p>
            <p><strong>Care Manager Code:</strong> ${patient.care_manager_user_code}</p>
        `;
        patientList.appendChild(item);
    });
}

function updateDashboardLinks(user) {
    const addHealthLink = document.getElementById("addHealthLink");
    const emergencyLink = document.getElementById("emergencyLink");
    const careManagerPanel = document.getElementById("careManagerPanel");
    const careManagerActions = document.getElementById("careManagerActions");
    const parentActions = document.getElementById("parentActions");

    if (addHealthLink) {
        addHealthLink.classList.toggle("hidden", user.role !== "care_manager");
    }

    if (emergencyLink) {
        emergencyLink.classList.toggle("hidden", user.role !== "parent");
    }

    if (careManagerPanel) {
        careManagerPanel.classList.toggle("hidden", user.role !== "care_manager");
    }

    if (careManagerActions) {
        careManagerActions.classList.toggle("hidden", user.role !== "care_manager");
    }

    if (parentActions) {
        parentActions.classList.toggle("hidden", user.role !== "parent");
    }
}

function setupLoginPage() {
    if (getToken()) {
        window.location.href = "dashboard.html";
        return;
    }

    const form = document.getElementById("loginForm");
    form.addEventListener("submit", handleLogin);
}

async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();

    try {
        const data = await apiRequest("/auth/login", "POST", { email, password });
        saveSession(data.access_token, data.user);
        setMessage("loginMessage", "Login successful. Redirecting...");
        window.location.href = "dashboard.html";
    } catch (error) {
        setMessage("loginMessage", error.message, true);
    }
}

function setupRegisterPage() {
    if (getToken()) {
        window.location.href = "dashboard.html";
        return;
    }

    const form = document.getElementById("registerForm");
    const roleSelect = document.getElementById("registerRole");

    toggleCareManagerSecretField();
    roleSelect.addEventListener("change", toggleCareManagerSecretField);
    form.addEventListener("submit", handleRegister);
}

async function handleRegister(event) {
    event.preventDefault();

    const payload = {
        name: document.getElementById("registerName").value.trim(),
        email: document.getElementById("registerEmail").value.trim(),
        password: document.getElementById("registerPassword").value.trim(),
        role: document.getElementById("registerRole").value,
        care_manager_secret: document.getElementById("careManagerSecret")
            ? document.getElementById("careManagerSecret").value.trim()
            : ""
    };

    try {
        const data = await apiRequest("/auth/register", "POST", payload);
        setMessage("registerMessage", `Registration successful. Your code is ${data.user_code}.`);
        document.getElementById("registerForm").reset();
        toggleCareManagerSecretField();
    } catch (error) {
        setMessage("registerMessage", error.message, true);
    }
}

async function setupDashboardPage() {
    if (!requireLogin()) {
        return;
    }

    const user = getUser();
    document.getElementById("welcomeText").textContent = `Welcome, ${user.name}`;
    document.getElementById("roleInfo").textContent = `You are logged in as ${formatRole(user.role)} with code ${user.user_code}.`;
    updateDashboardLinks(user);

    try {
        const patients = await loadPatients();
        renderPatients(document.getElementById("patientList"), patients);
    } catch (error) {
        document.getElementById("patientList").innerHTML = `<p>${error.message}</p>`;
    }

    const patientForm = document.getElementById("patientForm");
    if (patientForm) {
        patientForm.addEventListener("submit", handlePatientCreate);
    }
}

async function handlePatientCreate(event) {
    event.preventDefault();

    if (!requireRole(["care_manager"])) {
        return;
    }

    const payload = {
        name: document.getElementById("patientName").value.trim(),
        age: Number(document.getElementById("patientAge").value),
        parent_user_code: document.getElementById("parentUserCode").value.trim().toUpperCase(),
        child_user_code: document.getElementById("childUserCode").value.trim().toUpperCase() || null
    };

    try {
        const data = await apiRequest("/api/patients", "POST", payload);
        setMessage("patientFormMessage", `Patient added successfully. New patient code: ${data.patient_code}`);
        document.getElementById("patientForm").reset();
        const patients = await loadPatients();
        renderPatients(document.getElementById("patientList"), patients);
    } catch (error) {
        setMessage("patientFormMessage", error.message, true);
    }
}

async function setupAddHealthPage() {
    if (!requireLogin() || !requireRole(["care_manager"])) {
        return;
    }

    try {
        const patients = await loadPatients();
        fillPatientSelect("healthPatientId", patients, "Select a patient");
    } catch (error) {
        setMessage("healthMessage", error.message, true);
    }

    document.getElementById("healthForm").addEventListener("submit", handleHealthSubmit);
}

async function handleHealthSubmit(event) {
    event.preventDefault();

    const payload = {
        patient_id: document.getElementById("healthPatientId").value,
        heart_rate: Number(document.getElementById("heartRate").value),
        oxygen_level: Number(document.getElementById("oxygenLevel").value),
        systolic_bp: Number(document.getElementById("systolicBp").value),
        diastolic_bp: Number(document.getElementById("diastolicBp").value),
        notes: document.getElementById("healthNotes").value.trim()
    };

    try {
        const data = await apiRequest("/api/health", "POST", payload);
        setMessage("healthMessage", `Health record saved. Alerts created: ${data.alerts_created}`);
        document.getElementById("healthForm").reset();
    } catch (error) {
        setMessage("healthMessage", error.message, true);
    }
}

async function setupAlertsPage() {
    if (!requireLogin()) {
        return;
    }

    const alertList = document.getElementById("alertList");

    try {
        const data = await apiRequest("/api/alerts");
        renderAlerts(alertList, data.alerts || []);
    } catch (error) {
        alertList.innerHTML = `<p>${error.message}</p>`;
    }
}

function renderAlerts(alertList, alerts) {
    alertList.innerHTML = "";

    if (alerts.length === 0) {
        alertList.innerHTML = "<p>No alerts found.</p>";
        return;
    }

    alerts.forEach((alert) => {
        const item = document.createElement("div");
        item.className = "list-item";
        item.innerHTML = `
            <p><span class="badge badge-${alert.severity}">${alert.severity.toUpperCase()}</span></p>
            <p><strong>Patient Code:</strong> ${alert.patient_id}</p>
            <p><strong>Message:</strong> ${alert.message}</p>
            <p><strong>Created:</strong> ${formatDate(alert.created_at)}</p>
        `;
        alertList.appendChild(item);
    });
}

async function setupPatientDataPage() {
    if (!requireLogin()) {
        return;
    }

    try {
        const patients = await loadPatients();
        fillPatientSelect("patientSelect", patients, "Select a patient");
    } catch (error) {
        document.getElementById("patientInfo").innerHTML = `<p>${error.message}</p>`;
    }

    document.getElementById("loadPatientButton").addEventListener("click", loadSelectedPatientData);
}

async function loadSelectedPatientData() {
    const patientId = document.getElementById("patientSelect").value;
    if (!patientId) {
        document.getElementById("patientInfo").innerHTML = "<p>Please select a patient.</p>";
        return;
    }

    try {
        const data = await apiRequest(`/api/patient/${patientId}`);
        renderPatientInfo(data.patient);
        renderHealthHistory(data.health_records || []);
    } catch (error) {
        document.getElementById("patientInfo").innerHTML = `<p>${error.message}</p>`;
        document.getElementById("healthHistory").innerHTML = "";
    }
}

function renderPatientInfo(patient) {
    const container = document.getElementById("patientInfo");
    container.innerHTML = `
        <div class="list-item">
            <p><strong>Name:</strong> ${patient.name}</p>
            <p><strong>Age:</strong> ${patient.age}</p>
            <p><strong>Patient Code:</strong> ${patient.patient_code}</p>
            <p><strong>Parent Code:</strong> ${patient.parent_user_code}</p>
            <p><strong>Child Code:</strong> ${patient.child_user_code || "Not linked"}</p>
            <p><strong>Care Manager Code:</strong> ${patient.care_manager_user_code}</p>
        </div>
    `;
}

function renderHealthHistory(records) {
    const container = document.getElementById("healthHistory");
    container.innerHTML = "";

    if (records.length === 0) {
        container.innerHTML = "<p>No health records found.</p>";
        return;
    }

    records.forEach((record) => {
        const item = document.createElement("div");
        item.className = "list-item";
        item.innerHTML = `
            <p><strong>Patient Code:</strong> ${record.patient_id}</p>
            <p><strong>Heart Rate:</strong> ${record.heart_rate} bpm</p>
            <p><strong>Oxygen:</strong> ${record.oxygen_level}%</p>
            <p><strong>Blood Pressure:</strong> ${record.systolic_bp}/${record.diastolic_bp}</p>
            <p><strong>Notes:</strong> ${record.notes || "No notes"}</p>
            <p><strong>Created:</strong> ${formatDate(record.created_at)}</p>
        `;
        container.appendChild(item);
    });
}

async function setupEmergencyPage() {
    if (!requireLogin() || !requireRole(["parent"])) {
        return;
    }

    try {
        const patients = await loadPatients();
        fillPatientSelect("emergencyPatientId", patients, "Select a patient");
    } catch (error) {
        setMessage("emergencyStatus", error.message, true);
    }

    document.getElementById("emergencyForm").addEventListener("submit", handleEmergencySubmit);
}

async function handleEmergencySubmit(event) {
    event.preventDefault();

    const payload = {
        patient_id: document.getElementById("emergencyPatientId").value,
        message: document.getElementById("emergencyMessage").value.trim()
    };

    try {
        await apiRequest("/api/emergency", "POST", payload);
        setMessage("emergencyStatus", "Emergency alert sent successfully.");
        document.getElementById("emergencyForm").reset();
    } catch (error) {
        setMessage("emergencyStatus", error.message, true);
    }
}
