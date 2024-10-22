$(document).ready(() => {
    function toggleServiceDeletion(serviceId, serviceName) {
		$('#delete-confirmation-box form').prop('action', `/admin/delete_service/${serviceId}`);
		$('#service-name').html(serviceName);
		$('#delete-confirmation-box').show();
	}	

	// Call deletion function
	$('.toggle-service-deletion-btn').click(function (e) {
		e.stopPropagation();
		e.preventDefault();

		const serviceSlug = $(this).data('service-slug');
		const serviceName = $(this).data('service-name');

		toggleServiceDeletion(serviceSlug, serviceName);
	})
	
	// Call cancel function
	$('#cancel-deletion-btn').click(() => {
		$('#delete-confirmation-box').hide();		
	})
});