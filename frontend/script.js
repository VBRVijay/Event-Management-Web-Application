// Auto-detect API base URL for Docker environment
const API_BASE =
  window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:5000/api"
    : "/api";

// Global state
let currentEvents = [];
let currentAttendees = [];

// Navigation
function showSection(sectionId) {
  // Hide all sections
  document.querySelectorAll(".section").forEach((section) => {
    section.classList.remove("active");
  });

  // Remove active class from all nav buttons
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.classList.remove("active");
  });

  // Show selected section and activate button
  document.getElementById(sectionId).classList.add("active");
  event.target.classList.add("active");

  // Load section data
  switch (sectionId) {
    case "events":
      loadEvents();
      break;
    case "attendees":
      loadAttendees();
      break;
    case "reports":
      loadSalesReport();
      break;
  }
}

// ---------------- EVENT MANAGEMENT ---------------- //

async function loadEvents() {
  try {
    showNotification("Loading events...", "info");
    const response = await fetch(`${API_BASE}/events`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const events = await response.json();
    currentEvents = events;
    displayEvents(events);
    showNotification("Events loaded successfully!", "success");
  } catch (error) {
    console.error("Error loading events:", error);
    showNotification("Error loading events: " + error.message, "error");
  }
}

function displayEvents(events) {
  const container = document.getElementById("eventsList");
  if (events.length === 0) {
    container.innerHTML =
      '<p>No events found. <button class="btn btn-primary" onclick="seedSampleData()">Load Sample Data</button></p>';
    return;
  }

  container.innerHTML = events
    .map(
      (event) => `
        <div class="card">
          <h3>${event.title}</h3>
          <p><strong>Date:</strong> ${new Date(event.date).toLocaleString()}</p>
          <p><strong>Location:</strong> ${event.location}</p>
          <p><strong>Capacity:</strong> ${event.capacity}</p>
          <p><strong>Tickets Sold:</strong> ${event.tickets_sold}</p>
          <p><strong>Available:</strong> ${event.tickets_available}</p>
          <p>${event.description}</p>
          <div class="card-actions">
              <button class="btn btn-primary" onclick="editEvent(${event.id})">Edit</button>
              <button class="btn btn-danger" onclick="deleteEvent(${event.id})">Delete</button>
          </div>
        </div>`
    )
    .join("");
}

async function seedSampleData() {
  try {
    const response = await fetch(`${API_BASE}/seed`, { method: "POST" });
    if (response.ok) {
      showNotification("Sample data loaded successfully!", "success");
      loadEvents();
    } else {
      const error = await response.json();
      showNotification(error.error, "error");
    }
  } catch (error) {
    showNotification("Error loading sample data: " + error.message, "error");
  }
}

// Search Events
async function searchEvents() {
  const title = document.getElementById("searchTitle").value;
  const date = document.getElementById("searchDate").value;

  let url = `${API_BASE}/events?`;
  const params = [];
  if (title) params.push(`title=${encodeURIComponent(title)}`);
  if (date) params.push(`date=${date}`);
  url += params.join("&");

  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const events = await response.json();
    displayEvents(events);
    showNotification(`Found ${events.length} events`, "success");
  } catch (error) {
    showNotification("Error searching events: " + error.message, "error");
  }
}

function clearSearch() {
  document.getElementById("searchTitle").value = "";
  document.getElementById("searchDate").value = "";
  loadEvents();
}

// Event Modal Functions
function openEventModal(eventId = null) {
  const modal = document.getElementById("eventModal");
  const title = document.getElementById("eventModalTitle");
  const form = document.getElementById("eventForm");
  form.reset();

  if (eventId) {
    title.textContent = "Edit Event";
    document.getElementById("eventId").value = eventId;
    populateEventForm(eventId);
  } else {
    title.textContent = "Create Event";
    document.getElementById("eventId").value = "";
  }

  modal.style.display = "block";
}

function closeEventModal() {
  document.getElementById("eventModal").style.display = "none";
}

async function populateEventForm(eventId) {
  try {
    const response = await fetch(`${API_BASE}/events/${eventId}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const event = await response.json();
    document.getElementById("eventTitle").value = event.title;
    document.getElementById("eventDescription").value = event.description || "";
    document.getElementById("eventDate").value = event.date.slice(0, 16);
    document.getElementById("eventLocation").value = event.location;
    document.getElementById("eventCapacity").value = event.capacity;
  } catch (error) {
    showNotification("Error loading event: " + error.message, "error");
  }
}

document.getElementById("eventForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const eventId = document.getElementById("eventId").value;
  const formData = {
    title: document.getElementById("eventTitle").value,
    description: document.getElementById("eventDescription").value,
    date: document.getElementById("eventDate").value,
    location: document.getElementById("eventLocation").value,
    capacity: parseInt(document.getElementById("eventCapacity").value),
  };

  try {
    const url = eventId ? `${API_BASE}/events/${eventId}` : `${API_BASE}/events`;
    const method = eventId ? "PUT" : "POST";

    const response = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    if (response.ok) {
      closeEventModal();
      loadEvents();
      showNotification(`Event ${eventId ? "updated" : "created"} successfully!`, "success");
    } else {
      const error = await response.json();
      showNotification(error.error, "error");
    }
  } catch (error) {
    showNotification("Error saving event: " + error.message, "error");
  }
});

async function editEvent(eventId) {
  openEventModal(eventId);
}

async function deleteEvent(eventId) {
  if (!confirm("Are you sure you want to delete this event? This will also delete all associated attendees.")) return;

  try {
    const response = await fetch(`${API_BASE}/events/${eventId}`, { method: "DELETE" });
    if (response.ok) {
      loadEvents();
      showNotification("Event deleted successfully!", "success");
    } else {
      const error = await response.json();
      showNotification(error.error, "error");
    }
  } catch (error) {
    showNotification("Error deleting event: " + error.message, "error");
  }
}

// ---------------- ATTENDEE MANAGEMENT ---------------- //

async function loadAttendees() {
  try {
    const eventsResponse = await fetch(`${API_BASE}/events`);
    if (!eventsResponse.ok) throw new Error(`HTTP error! status: ${eventsResponse.status}`);
    const events = await eventsResponse.json();
    currentEvents = events;

    const allAttendees = [];
    for (const event of events) {
      const attendeesResponse = await fetch(`${API_BASE}/events/${event.id}/attendees`);
      if (attendeesResponse.ok) {
        const attendees = await attendeesResponse.json();
        attendees.forEach((a) => (a.event_title = event.title));
        allAttendees.push(...attendees);
      }
    }

    currentAttendees = allAttendees;
    displayAttendees(allAttendees);
  } catch (error) {
    showNotification("Error loading attendees: " + error.message, "error");
  }
}

function displayAttendees(attendees) {
  const container = document.getElementById("attendeesList");
  if (attendees.length === 0) {
    container.innerHTML = "<p>No attendees found.</p>";
    return;
  }

  container.innerHTML = attendees
    .map(
      (attendee) => `
        <div class="card">
            <h3>${attendee.name}</h3>
            <p><strong>Email:</strong> ${attendee.email}</p>
            <p><strong>Phone:</strong> ${attendee.phone || "N/A"}</p>
            <p><strong>Event:</strong> ${attendee.event_title}</p>
            <p><strong>Registered:</strong> ${new Date(attendee.registration_date).toLocaleDateString()}</p>
            <div class="card-actions">
                <button class="btn btn-primary" onclick="editAttendee(${attendee.id})">Edit</button>
            </div>
        </div>`
    )
    .join("");
}
// ... (continues with attendee modal, report, CSV import, and notifications as in your original file)