// Teacher dashboard data management

let teacherCourses = [];
let teacherStudents = [];
let teacherEvents = [];

// Load teacher statistics
async function loadTeacherStats() {
    try {
        // Load courses
        const coursesResponse = await fetch('http://localhost:8002/courses', {
            headers: Auth.getAuthHeader()
        });
        
        if (coursesResponse.ok) {
            teacherCourses = await coursesResponse.json();
            document.getElementById('stats-courses')?.textContent = teacherCourses.length;
            displayCourses(); // Display courses in the list
        }
        
        // Load students
        const studentsResponse = await fetch('http://localhost:8001/all-users');
        
        if (studentsResponse.ok) {
            const allUsers = await studentsResponse.json();
            teacherStudents = allUsers.filter(u => u.role === 'student');
            document.getElementById('stats-students')?.textContent = teacherStudents.length;
        }
        
        // Load resources (same as courses for now)
        document.getElementById('stats-resources')?.textContent = teacherCourses.length;
        
    } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
    }
}

// Display courses in the list
function displayCourses() {
    const coursesList = document.getElementById('courses-list');
    if (!coursesList) return;
    
    if (teacherCourses.length === 0) {
        coursesList.innerHTML = `
            <div class="col-span-3 text-center py-12">
                <svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                </svg>
                <p class="text-gray-500">Aucun cours pour le moment</p>
            </div>
        `;
        return;
    }
    
    const colors = [
        'from-blue-600 to-blue-700',
        'from-purple-600 to-purple-700',
        'from-emerald-500 to-emerald-600',
        'from-pink-600 to-pink-700',
        'from-indigo-600 to-indigo-700',
        'from-orange-500 to-orange-600'
    ];
    
    coursesList.innerHTML = teacherCourses.map((course, index) => {
        const color = colors[index % colors.length];
        const date = new Date(course.created_at).toLocaleDateString('fr-FR');
        
        return `
            <div class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow animate-slide-up" style="animation-delay:${index * 100}ms">
                <div class="h-24 bg-gradient-to-br ${color} p-4 flex items-end">
                    <h3 class="text-white font-bold">${course.title}</h3>
                </div>
                <div class="p-4">
                    <p class="text-sm text-gray-600 mb-2">${course.description}</p>
                    <div class="flex items-center justify-between text-xs text-gray-400 mb-2">
                        <span class="flex items-center gap-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
                            </svg>
                            ${course.filiere || 'Général'}
                        </span>
                        <span>Créé le ${date}</span>
                    </div>
                    ${course.file_name ? `
                        <div class="flex items-center gap-2 text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                            </svg>
                            ${course.file_name}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// Load teacher events
async function loadTeacherEvents() {
    const user = Auth.getUser();
    
    try {
        const response = await fetch(`http://localhost:8004/events/${user.username}`);
        
        if (response.ok) {
            teacherEvents = await response.json();
            console.log('Événements chargés:', teacherEvents.length);
            displayCalendarEvents();
        }
    } catch (error) {
        console.error('Erreur lors du chargement des événements:', error);
    }
}

// Display events on calendar
function displayCalendarEvents() {
    // This would update the calendar display
    // For now, just log the events
    console.log('Events to display:', teacherEvents);
}

// Handle event form submission
async function handleEventFormSubmit(e) {
    e.preventDefault();
    
    const user = Auth.getUser();
    const form = e.target;
    
    const title = form.querySelector('#event-title').value;
    const date = form.querySelector('#event-date').value;
    const startTime = form.querySelector('#event-start-time').value;
    const endTime = form.querySelector('#event-end-time').value;
    const type = form.querySelector('#event-type').value;
    const description = form.querySelector('#event-description').value;
    
    // Combine date and time
    const startDate = new Date(`${date}T${startTime}`);
    const endDate = new Date(`${date}T${endTime}`);
    
    const eventData = {
        title,
        description,
        event_type: type,
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString()
    };
    
    try {
        const response = await fetch(`http://localhost:8004/events?username=${user.username}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(eventData)
        });
        
        if (response.ok) {
            const newEvent = await response.json();
            teacherEvents.push(newEvent);
            showToast('Événement créé avec succès !', 'success');
            closeEventModal();
            form.reset();
            await loadTeacherEvents();
        } else {
            const error = await response.json();
            showToast('Erreur: ' + (error.detail || 'Erreur inconnue'), 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('Erreur lors de la création de l\'événement', 'error');
    }
}

// Initialize event form
function initEventForm() {
    const form = document.getElementById('event-form');
    if (form) {
        form.addEventListener('submit', handleEventFormSubmit);
    }
}

// Handle course form submission
async function handleCourseFormSubmit(e) {
    e.preventDefault();
    console.log('Course form submitted');
    
    const user = Auth.getUser();
    const form = e.target;
    
    const name = form.querySelector('#course-name').value;
    const description = form.querySelector('#course-description').value;
    const filiere = form.querySelector('#course-filiere').value;
    const fileInput = form.querySelector('#course-file');
    
    console.log('Course data:', { name, description, filiere, hasFile: fileInput.files.length > 0 });
    
    const formData = new FormData();
    formData.append('title', name);
    formData.append('description', description);
    formData.append('filiere', filiere);
    formData.append('teacher_username', user.username);
    
    if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
    }
    
    try {
        const authHeader = Auth.getAuthHeader();
        console.log('Sending request to /courses...');
        const response = await fetch('http://localhost:8002/courses', {
            method: 'POST',
            headers: {
                'Authorization': authHeader.Authorization
            },
            body: formData
        });
        
        console.log('Response status:', response.status);
        
        if (response.ok) {
            const result = await response.json();
            console.log('Course created:', result);
            showToast('Cours créé avec succès !', 'success');
            closeCourseModal();
            form.reset();
            await loadTeacherStats();
        } else {
            const error = await response.json();
            console.error('Error response:', error);
            showToast('Erreur: ' + (error.detail || 'Erreur inconnue'), 'error');
        }
    } catch (error) {
        console.error('Exception:', error);
        showToast('Erreur lors de la création du cours', 'error');
    }
}

// Handle assignment form submission
async function handleAssignmentFormSubmit(e) {
    e.preventDefault();
    
    const user = Auth.getUser();
    const form = e.target;
    
    const title = form.querySelector('#assignment-title').value;
    const description = form.querySelector('#assignment-description').value;
    const deadline = form.querySelector('#assignment-deadline').value;
    const filiere = form.querySelector('#assignment-filiere').value;
    
    const assignmentData = {
        title,
        description,
        deadline,
        filiere,
        teacher_username: user.username,
        status: 'active'
    };
    
    try {
        // Note: You'll need to create this endpoint in your backend
        const response = await fetch('http://localhost:8004/assignments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...Auth.getAuthHeader()
            },
            body: JSON.stringify(assignmentData)
        });
        
        if (response.ok) {
            showToast('Devoir créé avec succès !', 'success');
            closeAssignmentModal();
            form.reset();
            // Reload assignments if needed
        } else {
            const error = await response.json();
            showToast('Erreur: ' + (error.detail || 'Erreur inconnue'), 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('Erreur lors de la création du devoir', 'error');
    }
}

// Initialize course form
function initCourseForm() {
    const form = document.getElementById('course-form');
    if (form) {
        // Remove existing listener to avoid duplicates
        form.removeEventListener('submit', handleCourseFormSubmit);
        form.addEventListener('submit', handleCourseFormSubmit);
        console.log('Course form initialized');
    } else {
        console.warn('Course form not found');
    }
}

// Initialize assignment form
function initAssignmentForm() {
    const form = document.getElementById('assignment-form');
    if (form) {
        // Remove existing listener to avoid duplicates
        form.removeEventListener('submit', handleAssignmentFormSubmit);
        form.addEventListener('submit', handleAssignmentFormSubmit);
        console.log('Assignment form initialized');
    } else {
        console.warn('Assignment form not found');
    }
}

// Handle course upload
async function handleCourseUpload(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    try {
        const response = await fetch('http://localhost:8002/courses', {
            method: 'POST',
            headers: Auth.getAuthHeader(),
            body: formData
        });
        
        if (response.ok) {
            showToast('Cours ajouté avec succès !', 'success');
            form.reset();
            await loadTeacherStats();
        } else {
            const error = await response.json();
            showToast('Erreur: ' + (error.detail || 'Erreur inconnue'), 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('Erreur lors de l\'ajout du cours', 'error');
    }
}

// Initialize teacher dashboard
function initTeacherDashboard() {
    loadTeacherStats();
    loadTeacherEvents();
    
    // Set default date to today
    const dateInput = document.getElementById('event-date');
    if (dateInput && !dateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
    
    // Initialize all forms
    initEventForm();
    initCourseForm();
    initAssignmentForm();
}

// Export functions for global access
window.loadTeacherStats = loadTeacherStats;
window.loadTeacherEvents = loadTeacherEvents;
window.displayCourses = displayCourses;
window.initEventForm = initEventForm;
window.initCourseForm = initCourseForm;
window.initAssignmentForm = initAssignmentForm;
window.handleCourseUpload = handleCourseUpload;
window.initTeacherDashboard = initTeacherDashboard;
window.closeCourseModal = closeCourseModal;
window.closeAssignmentModal = closeAssignmentModal;
