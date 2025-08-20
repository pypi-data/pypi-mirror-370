
# HTML and CSS for the calendar button and popup
calendar_html = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>

<style>
  /* Style for the calendar button */
  .calendar-btn {
    background-color: white;
    border: 1px solid gray;
    border-radius: 3px;
    padding: 5px;
    font-size: 16px;
    cursor: pointer;
    position: fixed;  /* Changed from absolute to fixed */
    bottom: 50px;     /* Adjust position relative to the viewport */
    left: 10px;       /* Adjust position relative to the viewport */
    z-index: 10000;   /* Ensure it stays on top of other elements */
  }

  /* Calendar popup with sufficient size */
  .calendar-popup {
    display: none;
    position: fixed;  /* Keep the popup fixed so it stays in view */
    bottom: 100px;
    left: 10px;
    background-color: white;
    padding: 10px;
    border: 1px solid gray;
    border-radius: 3px;
    z-index: 10000;   /* Ensure it stays on top of other elements */
    width: 250px;
    height: 300px;
  }

  /* Ensure the calendar fits properly */
  #calendar {
    width: 100%;
    height: auto;
  }
</style>

<!-- Calendar Button -->
<div class="calendar-btn">📅 Select Date</div>

<!-- Calendar Popup -->
<div class="calendar-popup" id="calendar-popup">
  <div id="calendar"></div>
</div>

<script>
  // Initialize Flatpickr calendar
  const today = new Date().toISOString().split('T')[0];
  // Function to show the "Please wait" message
  function showLoadingMessage() {
    let loadingMessage = document.createElement("div");
    loadingMessage.id = "loading-message";
    loadingMessage.style.position = "fixed";
    loadingMessage.style.top = "50%";
    loadingMessage.style.left = "50%";
    loadingMessage.style.transform = "translate(-50%, -50%)";
    loadingMessage.style.backgroundColor = "rgba(0, 0, 0, 0.8)";
    loadingMessage.style.color = "white";
    loadingMessage.style.padding = "20px";
    loadingMessage.style.borderRadius = "5px";
    loadingMessage.style.zIndex = "9999";
    loadingMessage.innerText = "Please wait...";
    document.body.appendChild(loadingMessage);
  }

  // Function to remove the "Please wait" message
  function removeLoadingMessage() {
    let loadingMessage = document.getElementById("loading-message");
    if (loadingMessage) {
      loadingMessage.remove();
    }
  }


  flatpickr("#calendar", {
    inline: true,  // Render the calendar inline within the container
    maxDate: today,  // Disable future dates
    onChange: function(selectedDates, dateStr, instance) {
      console.log("Selected date: " + dateStr);  // Debugging: Log the selected date
      // Get the current URL and create a URL object to manipulate the query parameters
      // Get the current URL from the parent window
      showLoadingMessage();
      let currentUrl = window.parent.location.href;

      // If the URL contains "srcdoc", remove it and use the correct base path
      if (currentUrl.includes("srcdoc")) {
        currentUrl = currentUrl.replace("srcdoc", "");
      }

      const url = new URL(currentUrl);

      // Set or update the 'date' parameter while preserving existing parameters
      url.searchParams.set('date', dateStr);

      console.log("Updated URL: " + url.toString());  // Debugging: Log the updated URL

      // Update the parent window's location with the new URL
      window.parent.location.href = url.toString();
    }
  });
  // Remove the "Please wait" message once the page has finished loading
  window.addEventListener("load", function() {
    removeLoadingMessage();
  });

  // Toggle the calendar popup when the button is clicked
  document.querySelector(".calendar-btn").addEventListener("click", function() {
    var popup = document.getElementById("calendar-popup");
    if (popup.style.display === "none" || popup.style.display === "") {
      popup.style.display = "block";
    } else {
      popup.style.display = "none";
    }
  });
</script>
"""
