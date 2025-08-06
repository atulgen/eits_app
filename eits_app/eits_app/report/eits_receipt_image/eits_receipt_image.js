// JavaScript file for EITS Receipt Report
// This should be saved as the same name as your report Python file but with .js extension

frappe.query_reports["EITS Receipt Image"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 0
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 0
        },
        {
            "fieldname": "paid_by",
            "label": __("Paid By"),
            "fieldtype": "Data",
            "reqd": 0
        },
        {
            "fieldname": "paid_from",
            "label": __("Paid From"),
            "fieldtype": "Link",
            "options": "Customer",
            "reqd": 0
        },
        {
            "fieldname": "payment_method",
            "label": __("Payment Method"),
            "fieldtype": "Link",
            "options": "Method of Payment",
            "reqd": 0
        },
        {
            "fieldname": "bill_number",
            "label": __("Bill Number"),
            "fieldtype": "Data",
            "reqd": 0
        },
        {
            "fieldname": "only_with_images",
            "label": __("Only Show Records with Images"),
            "fieldtype": "Check",
            "default": 0,
            "reqd": 0
        }
    ],
    
    // Add formatter to make the Actions column clickable
    "formatter": function(value, row, column, data, default_formatter) {
        // Make Receipt ID clickable to open the document
        if (column.fieldname === "name") {
            return `<a href="/app/receipt-eits/${value}" target="_blank">${value}</a>`;
        }
        // Make View Images clickable with a proper button
        if (column.fieldname === "view_images" && value === "View Images") {
            return `<button class="btn btn-sm" onclick="view_receipt_images('${data.name}'); return false;" style="cursor: pointer;">
                        <i class="fa fa-eye"></i> View Images
                    </button>`;
        }
        // Make Submit button clickable
        if (column.fieldname === "submit_action") {
            if (value === "Submit") {
                return `<button class="btn btn-sm" onclick="submit_receipt('${data.name}'); return false;" style="cursor: pointer;">
                            <i class="fa fa-check"></i> Submit
                        </button>`;
            } else if (value === "Submitted") {
                return `<span class="badge badge-success" style="padding: 5px 10px;">
                            <i class="fa fa-check-circle"></i> Submitted
                        </span>`;
            } else if (value === "Cancelled") {
                return `<span class="badge badge-danger" style="padding: 5px 10px;">
                            <i class="fa fa-times-circle"></i> Cancelled
                        </span>`;
            }
        }
        return default_formatter(value, row, column, data);
    }
};

// Function to submit receipt - THIS WAS MISSING IN YOUR ORIGINAL CODE
function submit_receipt(receipt_id) {
    // Show confirmation dialog
    frappe.confirm(
        __('Are you sure you want to submit receipt {0}?', [receipt_id]),
        function() {
            // Show loading message
            frappe.show_alert({
                message: __('Submitting receipt...'),
                indicator: 'blue'
            });

            // Call the server method
            frappe.call({
                method: "eits_app.eits_app.report.eits_receipt_image.eits_receipt_image.submit_receipt",
                args: {
                    receipt_id: receipt_id
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        // Show success message
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: 'green'
                        });
                        
                        // Refresh the report to show updated status
                        frappe.query_report.refresh();
                        
                    } else {
                        frappe.msgprint({
                            title: __("Error"),
                            message: r.message ? r.message.message : __("Failed to submit receipt. Please try again."),
                            indicator: "red"
                        });
                    }
                },
                error: function(r) {
                    console.error("Error submitting receipt:", r);
                    let error_message = __("Error submitting receipt: ");
                    
                    if (r.exc) {
                        // Extract the actual error message from exc
                        let exc_message = r.exc;
                        if (exc_message.includes('frappe.exceptions.')) {
                            exc_message = exc_message.split(':').slice(-1)[0].trim();
                        }
                        error_message += exc_message;
                    } else if (r.message) {
                        error_message += r.message;
                    } else {
                        error_message += __("Please try again or contact administrator.");
                    }
                    
                    frappe.msgprint({
                        title: __("Error"),
                        message: error_message,
                        indicator: "red"
                    });
                }
            });
        }
    );
}

// Function to fetch and display receipt images using server method
function view_receipt_images(receipt_id) {
    // Show loading message
    frappe.show_alert({
        message: __('Loading images...'),
        indicator: 'blue'
    });

    // Call the server method we added to the Python file
    frappe.call({
        method: "eits_app.eits_app.report.eits_receipt_image.eits_receipt_image.get_receipt_images",
        args: {
            receipt_id: receipt_id
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                show_image_dialog(receipt_id, r.message);
            } else {
                frappe.msgprint({
                    title: __("No Images"),
                    message: __("No images found for this receipt record."),
                    indicator: "orange"
                });
            }
        },
        error: function(r) {
            console.error("Error fetching images:", r);
            frappe.msgprint({
                title: __("Error"),
                message: __("Error loading images: ") + (r.exc || "Please try again or contact administrator."),
                indicator: "red"
            });
        }
    });
}

// Function to create and show the image carousel side panel
function show_image_dialog(receipt_id, images) {
    // Filter valid images
    let validImages = images.filter(img => 
        img.image && img.image !== '/files/' && img.image.trim() !== ''
    );
    
    if (validImages.length === 0) {
        frappe.msgprint({
            title: __("No Images"),
            message: __("No valid images found for this receipt record."),
            indicator: "orange"
        });
        return;
    }
    
    // Create side panel with carousel
    create_image_carousel_panel(receipt_id, validImages);
}

// Function to create the side panel image carousel
function create_image_carousel_panel(receipt_id, images) {
    // Remove existing panel if any
    $('.image-carousel-panel').remove();
    
    let currentIndex = 0;
    
    // Create the side panel HTML
    let panelHtml = `
        <div class="image-carousel-panel" style="
            position: fixed;
            top: 0;
            right: 0;
            width: 40%;
            height: 100vh;
            background: rgba(0, 0, 0, 0.95);
            z-index: 10000;
            display: flex;
            flex-direction: column;
            box-shadow: -5px 0 15px rgba(0, 0, 0, 0.3);
        ">
            <style>
                .carousel-header {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 15px 20px;
                    color: white;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                }
                .carousel-content {
                    flex: 1;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    position: relative;
                    padding: 20px;
                }
                .carousel-image {
                    max-width: 100%;
                    max-height: 70vh;
                    object-fit: contain;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
                }
                .carousel-nav {
                    position: absolute;
                    top: 50%;
                    transform: translateY(-50%);
                    background: rgba(255, 255, 255, 0.9);
                    border: none;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    font-size: 18px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.3s ease;
                    color: #333;
                }
                .carousel-nav:hover {
                    background: white;
                    transform: translateY(-50%) scale(1.1);
                }
                .carousel-nav:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                .carousel-nav.prev {
                    left: 10px;
                }
                .carousel-nav.next {
                    right: 10px;
                }
                .carousel-footer {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 15px 20px;
                    color: white;
                    border-top: 1px solid rgba(255, 255, 255, 0.2);
                }
                .image-counter {
                    background: rgba(0, 0, 0, 0.7);
                    color: white;
                    padding: 8px 15px;
                    border-radius: 20px;
                    position: absolute;
                    top: 20px;
                    left: 20px;
                    font-size: 14px;
                }
                .close-btn {
                    background: rgba(255, 255, 255, 0.2);
                    border: none;
                    color: white;
                    width: 35px;
                    height: 35px;
                    border-radius: 50%;
                    font-size: 18px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                .close-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                    transform: scale(1.1);
                }
                .image-remarks-panel {
                    background: rgba(255, 255, 255, 0.95);
                    color: #333;
                    padding: 10px 15px;
                    border-radius: 6px;
                    margin-top: 10px;
                    max-height: 100px;
                    overflow-y: auto;
                }
            </style>
            
            <!-- Header -->
            <div class="carousel-header">
                <div>
                    <h4 style="margin: 0; font-size: 18px;">Receipt Images: ${receipt_id}</h4>
                </div>
                <button class="close-btn" onclick="close_image_carousel()">&times;</button>
            </div>
            
            <!-- Content -->
            <div class="carousel-content">
                <div class="image-counter">
                    <span id="current-image-number">1</span> / ${images.length}
                </div>
                
                <button class="carousel-nav prev" id="prev-btn" onclick="change_image(-1)">
                    <i class="fa fa-chevron-left"></i>
                </button>
                
                <img id="carousel-image" class="carousel-image" src="${images[0].image}" alt="Receipt Image">
                
                <button class="carousel-nav next" id="next-btn" onclick="change_image(1)">
                    <i class="fa fa-chevron-right"></i>
                </button>
            </div>
            
            <!-- Footer -->
            <div class="carousel-footer">
                <div id="image-remarks">
                    ${images[0].remarks ? `
                        <div class="image-remarks-panel">
                            <strong><i class="fa fa-comment"></i> Remarks:</strong><br>
                            ${frappe.utils.escape_html(images[0].remarks)}
                        </div>
                    ` : '<div style="color: rgba(255,255,255,0.7); font-style: italic;">No remarks for this image</div>'}
                </div>
                <div style="margin-top: 10px; font-size: 12px; color: rgba(255,255,255,0.7);">
                    Use arrow keys or click buttons to navigate • ESC to close • Click outside to close
                </div>
            </div>
        </div>
    `;
    
    // Add panel to body
    $('body').append(panelHtml);
    
    // Add click handler to close when clicking outside the panel content
    $('.image-carousel-panel').on('click', function(e) {
        // Only close if clicking on the overlay (not the panel content)
        if (e.target === this) {
            close_image_carousel();
        }
    });
    
    // Prevent closing when clicking inside the panel content
    $('.carousel-panel-content').on('click', function(e) {
        e.stopPropagation();
    });
    
    // Store images data globally for navigation
    window.carouselImages = images;
    window.currentCarouselIndex = 0;
    
    // Update navigation buttons
    update_carousel_navigation();
    
    // Add keyboard navigation
    $(document).on('keydown.carousel', function(e) {
        if (e.keyCode === 37) { // Left arrow
            change_image(-1);
        } else if (e.keyCode === 39) { // Right arrow
            change_image(1);
        } else if (e.keyCode === 27) { // ESC
            close_image_carousel();
        }
    });
}

// Function to change image in carousel
function change_image(direction) {
    if (!window.carouselImages) return;
    
    let newIndex = window.currentCarouselIndex + direction;
    
    // Bounds checking
    if (newIndex < 0) newIndex = 0;
    if (newIndex >= window.carouselImages.length) newIndex = window.carouselImages.length - 1;
    
    // If index didn't change, do nothing
    if (newIndex === window.currentCarouselIndex) return;
    
    window.currentCarouselIndex = newIndex;
    let currentImage = window.carouselImages[newIndex];
    
    // Update image
    $('#carousel-image').attr('src', currentImage.image);
    
    // Update counter
    $('#current-image-number').text(newIndex + 1);
    
    // Update remarks
    let remarksHtml = currentImage.remarks ? `
        <div class="image-remarks-panel">
            <strong><i class="fa fa-comment"></i> Remarks:</strong><br>
            ${frappe.utils.escape_html(currentImage.remarks)}
        </div>
    ` : '<div style="color: rgba(255,255,255,0.7); font-style: italic;">No remarks for this image</div>';
    
    $('#image-remarks').html(remarksHtml);
    
    // Update navigation buttons
    update_carousel_navigation();
}

// Function to update navigation button states
function update_carousel_navigation() {
    if (!window.carouselImages) return;
    
    // Update prev button
    if (window.currentCarouselIndex === 0) {
        $('#prev-btn').prop('disabled', true).css('opacity', '0.5');
    } else {
        $('#prev-btn').prop('disabled', false).css('opacity', '1');
    }
    
    // Update next button
    if (window.currentCarouselIndex === window.carouselImages.length - 1) {
        $('#next-btn').prop('disabled', true).css('opacity', '0.5');
    } else {
        $('#next-btn').prop('disabled', false).css('opacity', '1');
    }
}

// Function to close the carousel panel
function close_image_carousel() {
    $('.image-carousel-panel').remove();
    $(document).off('keydown.carousel');
    window.carouselImages = null;
    window.currentCarouselIndex = 0;
}

// Additional utility function to test method paths (for debugging)
function test_submit_method(receipt_id) {
    console.log("Testing submit method for:", receipt_id);
    frappe.call({
        method: "eits_app.eits_app.report.eits_receipt_image.eits_receipt_image.submit_receipt",
        args: {
            receipt_id: receipt_id
        },
        callback: function(r) {
            console.log("Response:", r);
        },
        error: function(r) {
            console.error("Error:", r);
        }
    });
}

// Function to refresh report data
function refresh_report() {
    if (frappe.query_report) {
        frappe.query_report.refresh();
    }
}