function removeServiceImage(serviceId) {
    $.ajax({
        type: 'POST',
        url: `/admin/remove_service_image/${serviceId}`,
        dataType: 'json',
        success: (data) => {
            if (data.message) {
                console.log(data.message);
                $('#current-service-image').hide();
            };
        },
        error: (error) => {
            console.error("Error: ", error);
        },
    });
};

$('#current-service-image button').click(() => {
    removeServiceImage('{{service.pk}}');
});