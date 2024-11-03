function populateBlocks(stateName, districtName) {
    $.ajax({
        type: 'get',
        url: '/admin/get_blocks/',
        data: {
            'district_name': districtName,
            'state_name': stateName
        },
        dataType : 'json',
        success: data => {
            $('#block-dropdown').chosen('destroy');
            $('#block-dropdown').html(`<option label="Select Block"></option>`);
            if (data.blocks && Array.isArray(data.blocks)) {
                data.blocks.forEach(block => {
                    let html = `<option value="${block.block}">${block.block}</option>`
                    $('#block-dropdown').append(html);
                });
            } else {
                $('#block-dropdown').html(`<option label="Select Block"></option>`);
            };

            $('#block-dropdown').chosen();

        },
        error: (jqXHR, textStatus, errorThrow) => {
            console.log('Error: ', textStatus, errorThrow);
        }
    });
}

$(document).ready(() => {
    $('#district-dropdown').on('change', function() {
        const districtName = $(this).val();
        const stateName = $('#state-dropdown').val();
        
        populateBlocks(stateName, districtName);
    });

    if ($('#state-dropdown').val() && $('#district-dropdown').val()) {
        const districtName = $(this).val();
        const stateName = $('#state-dropdown').val();
        
        populateBlocks(stateName, districtName);
    }
});