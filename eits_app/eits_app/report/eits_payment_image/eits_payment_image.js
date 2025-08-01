// JavaScript file for EITS Payment Report
// This should be saved as the same name as your report Python file but with .js extension

frappe.query_reports["EITS Payment Image"] = {
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
            "fieldname": "paid_to",
            "label": __("Paid To"),
            "fieldtype": "Link",
            "options": "Supplier",
            "reqd": 0
        },
        {
            "fieldname": "payment_method",
            "label": __("Payment Method"),
            "fieldtype": "Link",
            "options": "Mode of Payment",
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
        // Make Payment ID clickable to open the document
        if (column.fieldname === "name") {
            return `<a href="/app/eits-payment/${value}" target="_blank">${value}</a>`;
        }
        // Make View Images clickable
        if (column.fieldname === "view_images" && value === "View Images") {
            return `<a href="#" onclick="open_payment_record('${data.name}'); return false;" style="color: #007bff; cursor: pointer;">${value}</a>`;
        }
        return default_formatter(value, row, column, data);
    }
};

// Simple function to open payment record
function open_payment_record(payment_id) {
    frappe.set_route("Form", "EITS Payment", payment_id);
}

// Alternative: If you want to try the server method approach, uncomment below and update the path
/*
function view_payment_images(payment_id) {
    frappe.call({
        method: "eits_app.eits_app.report.eits_payment_image.eits_payment_image.get_payment_images",
        args: {
            payment_id: payment_id
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                show_image_dialog(payment_id, r.message);
            } else {
                frappe.msgprint(__("No images found for this payment."));
            }
        },
        error: function(r) {
            frappe.msgprint(__("Error loading images. Please check your permissions."));
        }
    });
}

function show_image_dialog(payment_id, images) {
    let dialog_content = `<div class="image-gallery">`;
    
    images.forEach(function(img, index) {
        if (img.image && img.image !== '/files/') {
            dialog_content += `
                <div class="image-item" style="margin-bottom: 20px; text-align: center;">
                    <div style="margin-bottom: 10px;">
                        <img src="${img.image}" 
                             style="max-width: 100%; max-height: 400px; cursor: pointer; border: 1px solid #ddd; border-radius: 4px;" 
                             onclick="window.open('${img.image}', '_blank')"
                             title="Click to open in new tab">
                    </div>
                    ${img.remarks ? `<div class="text-muted"><strong>Remarks:</strong> ${img.remarks}</div>` : ''}
                </div>
            `;
        }
    });
    
    dialog_content += `</div>`;
    
    let d = new frappe.ui.Dialog({
        title: __('Images for Payment: {0}', [payment_id]),
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'images_html',
                options: dialog_content
            }
        ],
        size: 'large'
    });
    
    d.show();
}
*/
