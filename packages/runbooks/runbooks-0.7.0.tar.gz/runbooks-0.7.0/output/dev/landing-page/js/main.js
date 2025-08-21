/**
 * South Vietnam Travel Website - Main JavaScript
 * Generated from Figma design: High-fidelity
 */

// Initialize interactive features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Video player functionality
  initializeVideoPlayer();
  
  // Map interaction functionality
  initializeMap();
  
  // Image gallery lightbox
  initializeGallery();
  
  // Mobile navigation toggle
  initializeMobileNav();
});

function initializeVideoPlayer() {
  const videoButton = document.querySelector('.video-play-button');
  if (videoButton) {
    videoButton.addEventListener('click', function() {
      // Replace with actual video player implementation
      alert('Video player functionality will be implemented here');
    });
  }
}

function initializeMap() {
  const mapMarkers = document.querySelectorAll('.map-marker');
  if (mapMarkers.length) {
    mapMarkers.forEach(marker => {
      marker.addEventListener('click', function() {
        const locationId = this.getAttribute('data-location-id');
        // Show location information when marker is clicked
        showLocationInfo(locationId);
      });
    });
  }
}

function showLocationInfo(locationId) {
  // Hide all location info panels
  document.querySelectorAll('.location-info').forEach(panel => {
    panel.classList.remove('active');
  });
  
  // Show the selected location info
  const selectedInfo = document.querySelector(`.location-info[data-location-id="${locationId}"]`);
  if (selectedInfo) {
    selectedInfo.classList.add('active');
  }
}

function initializeGallery() {
  const galleryImages = document.querySelectorAll('.gallery-image');
  if (galleryImages.length) {
    galleryImages.forEach(image => {
      image.addEventListener('click', function() {
        const imgSrc = this.getAttribute('src');
        openLightbox(imgSrc);
      });
    });
  }
}

function openLightbox(imgSrc) {
  // Create lightbox elements
  const lightbox = document.createElement('div');
  lightbox.className = 'lightbox';
  
  const img = document.createElement('img');
  img.src = imgSrc;
  
  const closeBtn = document.createElement('button');
  closeBtn.className = 'lightbox-close';
  closeBtn.innerHTML = '&times;';
  closeBtn.addEventListener('click', () => {
    document.body.removeChild(lightbox);
  });
  
  lightbox.appendChild(closeBtn);
  lightbox.appendChild(img);
  
  document.body.appendChild(lightbox);
}

function initializeMobileNav() {
  const menuToggle = document.querySelector('.menu-toggle');
  const navMenu = document.querySelector('.nav-menu');
  
  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', function() {
      navMenu.classList.toggle('active');
      this.classList.toggle('active');
    });
  }
}
