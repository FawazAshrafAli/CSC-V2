function populateDistricts(stateName) {
    $.ajax({
        type: 'get',
        url: '/admin/get_districts/',
        data: {'state_name': stateName},
        dataType : 'json',
        success: data => {
            console.log(data);

            $('#district-dropdown').chosen('destroy');

            if ($('#district-dropdown-input')) {
                $('#district-dropdown-input').html(`<option label="Select District"></option>`);
            }

            $('#district-dropdown').html(`<option label="Select District"></option>`);
            if (data.districts && Array.isArray(data.districts)) {
                data.districts.forEach(district => {
                    let html = `<option value="${district.district}">${district.district}</option>`

                    if ($('#district-dropdown-input')) {
                        $('#district-dropdown-input').append(html);    
                    }

                    $('#district-dropdown').append(html);
                });
            } else {
                if ($('#district-dropdown-input')) {
                    $('#district-dropdown-input').html(`<option label="Select District"></option>`);
                }

                $('#district-dropdown').html(`<option label="Select District"></option>`);
            };

            $('#district-dropdown').chosen();

        },
        error: (jqXHR, textStatus, errorThrow) => {
            console.log('Error: ', textStatus, errorThrow);
        }
    });
};

$(document).ready(() => {
    $('#state-dropdown').on('change', function() {
        const stateName = $(this).val();
        populateDistricts(stateName);        
    });

    if ($('#state-dropdown').val()) {
        const stateName = $('#state-dropdown').val();
        populateDistricts(stateName); 
    }
});