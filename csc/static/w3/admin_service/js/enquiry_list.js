$(document).ready(function() {
    function toggleEnquiryDeletion(serviceId, serviceName) {
        $('#delete-confirmation-box form').prop('action', `/admin/delete_service_enquiry/${serviceId}`);
        $('#service-enquiry').html(serviceName);
        $('#delete-confirmation-box').show();
    }

    // Callin deletion function
    $('.toggle-service-enquiry-deletion-btn').click(function (e) {            
        e.preventDefault();
        const enquirySlug = $(this).data('enquiry-slug');
        const enquiryService = $(this).data('enquiry-service');

        toggleEnquiryDeletion(enquirySlug, enquiryService);
    });

    // Calling cancel function
    $('#cancel-deletion-btn').click(() => {
        $('#delete-confirmation-box').hide();		
    })
})