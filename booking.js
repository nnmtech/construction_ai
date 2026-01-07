/**
 * Construction AI - Demo Booking Frontend
 * 
 * This script handles all frontend functionality for the demo booking system:
 * - Loading available time slots from the API
 * - Validating form input
 * - Submitting booking requests
 * - Displaying success/error messages
 * - Managing UI state
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

const API_BASE_URL = 'http://localhost:8000/api/booking';
const SLOTS_ENDPOINT = `${API_BASE_URL}/available-slots`;
const SCHEDULE_ENDPOINT = `${API_BASE_URL}/schedule-demo`;

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

let appState = {
    slots: [],
    selectedSlotId: null,
    isLoading: false,
    isSubmitting: false
};

// ============================================================================
// DOM ELEMENTS
// ============================================================================

const form = document.getElementById('bookingForm');
const messageEl = document.getElementById('message');
const slotsContainer = document.getElementById('slotsContainer');
const slotsLoading = document.getElementById('slotsLoading');
const selectedSlotDisplay = document.getElementById('selectedSlotDisplay');
const selectedSlotText = document.getElementById('selectedSlotText');
const submitBtn = document.getElementById('submitBtn');

const companyNameInput = document.getElementById('companyName');
const contactNameInput = document.getElementById('contactName');
const emailInput = document.getElementById('email');
const phoneInput = document.getElementById('phone');
const contactMethodInput = document.getElementById('contactMethod');
const notesInput = document.getElementById('notes');

// ============================================================================
// MESSAGE DISPLAY
// ============================================================================

/**
 * Display a message to the user
 * @param {string} message - The message text
 * @param {string} type - Message type: 'success', 'error', 'info', 'warning'
 * @param {number} duration - How long to show the message (ms), 0 = permanent
 */
function showMessage(message, type = 'info', duration = 5000) {
    messageEl.textContent = message;
    messageEl.className = `message show ${type}`;

    if (duration > 0) {
        setTimeout(() => {
            messageEl.classList.remove('show');
        }, duration);
    }
}

/**
 * Clear the message display
 */
function clearMessage() {
    messageEl.classList.remove('show');
    messageEl.textContent = '';
}

// ============================================================================
// SLOT LOADING
// ============================================================================

/**
 * Load available time slots from the API
 */
async function loadAvailableSlots() {
    try {
        slotsLoading.style.display = 'flex';
        slotsContainer.innerHTML = '';
        clearMessage();

        console.log('Fetching available slots from:', SLOTS_ENDPOINT);

        const response = await fetch(SLOTS_ENDPOINT);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        console.log('Received slots:', data);

        appState.slots = data.slots;

        if (appState.slots.length === 0) {
            showMessage('No available slots at this time. Please try again later.', 'warning', 0);
            return;
        }

        renderSlots(data.slots);
        showMessage(`${data.total_slots} time slots available`, 'info', 3000);

    } catch (error) {
        console.error('Error loading slots:', error);
        showMessage(`Failed to load available times: ${error.message}`, 'error', 0);
    } finally {
        slotsLoading.style.display = 'none';
    }
}

/**
 * Render available slots grouped by date
 * @param {Array} slots - Array of slot objects
 */
function renderSlots(slots) {
    slotsContainer.innerHTML = '';

    // Group slots by date
    const slotsByDate = {};
    slots.forEach(slot => {
        if (!slotsByDate[slot.date]) {
            slotsByDate[slot.date] = [];
        }
        slotsByDate[slot.date].push(slot);
    });

    // Render each date group
    Object.keys(slotsByDate).sort().forEach(date => {
        const dateGroup = document.createElement('div');
        dateGroup.className = 'date-group';

        // Format date for display
        const dateObj = new Date(date + 'T00:00:00');
        const dateStr = dateObj.toLocaleDateString('en-US', {
            weekday: 'long',
            month: 'short',
            day: 'numeric'
        });

        const dateTitle = document.createElement('div');
        dateTitle.className = 'date-group-title';
        dateTitle.textContent = dateStr;
        dateGroup.appendChild(dateTitle);

        const slotsGrid = document.createElement('div');
        slotsGrid.className = 'slots-by-date';

        slotsByDate[date].forEach(slot => {
            const slotEl = document.createElement('div');
            slotEl.className = 'slot';

            if (!slot.available) {
                slotEl.classList.add('disabled');
            }

            if (slot.slot_id === appState.selectedSlotId) {
                slotEl.classList.add('selected');
            }

            slotEl.innerHTML = `
                <div class="slot-date">${slot.date}</div>
                <div class="slot-time">${slot.start_time}</div>
                <div class="slot-status">${slot.available ? 'Available' : 'Booked'}</div>
            `;

            if (slot.available) {
                slotEl.addEventListener('click', () => selectSlot(slot));
            }

            slotsGrid.appendChild(slotEl);
        });

        dateGroup.appendChild(slotsGrid);
        slotsContainer.appendChild(dateGroup);
    });
}

/**
 * Handle slot selection
 * @param {Object} slot - The selected slot object
 */
function selectSlot(slot) {
    appState.selectedSlotId = slot.slot_id;

    // Update display
    selectedSlotText.textContent = `${slot.date} at ${slot.start_time}`;
    selectedSlotDisplay.classList.add('show');

    // Update progress
    document.getElementById('step2').classList.add('completed');

    // Re-render slots to show selection
    renderSlots(appState.slots);

    showMessage('Time slot selected! Complete the form and click "Schedule My Demo"', 'success', 3000);
}

// ============================================================================
// FORM VALIDATION
// ============================================================================

/**
 * Validate form inputs
 * @returns {Object} - Validation result with isValid flag and errors array
 */
function validateForm() {
    const errors = [];

    // Validate company name
    if (!companyNameInput.value.trim()) {
        errors.push('Company name is required');
    }

    // Validate contact name
    if (!contactNameInput.value.trim()) {
        errors.push('Your name is required');
    }

    // Validate email
    if (!emailInput.value.trim()) {
        errors.push('Email address is required');
    } else if (!isValidEmail(emailInput.value)) {
        errors.push('Please enter a valid email address');
    }

    // Validate contact method
    if (!contactMethodInput.value) {
        errors.push('Please select a contact method');
    }

    // Validate slot selection
    if (!appState.selectedSlotId) {
        errors.push('Please select a time slot');
    }

    return {
        isValid: errors.length === 0,
        errors: errors
    };
}

/**
 * Check if email is valid
 * @param {string} email - Email to validate
 * @returns {boolean} - True if valid
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// ============================================================================
// FORM SUBMISSION
// ============================================================================

/**
 * Handle form submission
 * @param {Event} e - Form submit event
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    // Validate form
    const validation = validateForm();
    if (!validation.isValid) {
        const errorMessage = validation.errors.join('\n');
        showMessage(`Please fix the following errors:\n${errorMessage}`, 'error', 0);
        return;
    }

    // Prepare request data
    const requestData = {
        email: emailInput.value.trim(),
        slot_id: appState.selectedSlotId,
        preferred_contact_method: contactMethodInput.value,
        notes: notesInput.value.trim() || null
    };

    console.log('Submitting booking request:', requestData);

    // Disable submit button
    submitBtn.disabled = true;
    appState.isSubmitting = true;

    try {
        // Show loading state
        submitBtn.innerHTML = '<span class="spinner-text"><div class="loading"></div><span>Scheduling...</span></span>';

        // Send request
        const response = await fetch(SCHEDULE_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        console.log('Response status:', response.status);

        const data = await response.json();

        console.log('Response data:', data);

        if (!response.ok) {
            throw new Error(data.detail || `HTTP error! status: ${response.status}`);
        }

        // Success!
        showMessage(
            `✓ Demo scheduled successfully!\n\nYou'll receive a confirmation email at ${emailInput.value} with the Zoom link and details.`,
            'success',
            0
        );

        // Update progress
        document.getElementById('step3').classList.add('completed');

        // Reset form
        setTimeout(() => {
            form.reset();
            appState.selectedSlotId = null;
            selectedSlotDisplay.classList.remove('show');
            document.getElementById('step2').classList.remove('completed');
            document.getElementById('step3').classList.remove('completed');
            renderSlots(appState.slots);
        }, 2000);

    } catch (error) {
        console.error('Error scheduling demo:', error);
        showMessage(`Failed to schedule demo: ${error.message}`, 'error', 0);
    } finally {
        // Re-enable submit button
        submitBtn.disabled = false;
        appState.isSubmitting = false;
        submitBtn.innerHTML = 'Schedule My Demo';
    }
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    form.addEventListener('submit', handleFormSubmit);

    // Load slots when page loads
    window.addEventListener('load', loadAvailableSlots);

    // Reload slots button (optional)
    // You could add a "Refresh" button to reload slots
}

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize the application
 */
function initialize() {
    console.log('Initializing booking application...');
    initializeEventListeners();
    console.log('Application initialized');
}

// Start the application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Format date for display
 * @param {string} dateStr - Date string (YYYY-MM-DD)
 * @returns {string} - Formatted date
 */
function formatDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Format time for display
 * @param {string} timeStr - Time string (HH:MM)
 * @returns {string} - Formatted time
 */
function formatTime(timeStr) {
    const [hours, minutes] = timeStr.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
}

/**
 * Log message to console with timestamp
 * @param {string} message - Message to log
 * @param {string} level - Log level (info, warn, error)
 */
function log(message, level = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    console.log(`[${timestamp}] [${level.toUpperCase()}] ${message}`);
}

// ============================================================================
// ERROR HANDLING
// ============================================================================

/**
 * Global error handler
 */
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    showMessage('An unexpected error occurred. Please refresh the page and try again.', 'error', 0);
});

/**
 * Handle unhandled promise rejections
 */
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled rejection:', event.reason);
    showMessage('An unexpected error occurred. Please refresh the page and try again.', 'error', 0);
});

// ============================================================================
// EXPORT FOR TESTING
// ============================================================================

// These functions can be called from the browser console for testing
window.bookingApp = {
    loadSlots: loadAvailableSlots,
    selectSlot: selectSlot,
    validateForm: validateForm,
    getState: () => appState,
    showMessage: showMessage,
    clearMessage: clearMessage
};
